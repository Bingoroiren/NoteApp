
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import threading
import time
from plyer import notification

logger = logging.getLogger(__name__)


class ReminderController:
    """Controller for managing reminders"""
    
    def __init__(self, note_controller):
        self.note_controller = note_controller
        self.running = False
        self.check_interval = 60  # Check every minute
        self.reminder_thread = None
        self.notified_reminders = set()  # Track already notified reminders
    
    def start(self):
        """Start the reminder checking thread"""
        if not self.running:
            self.running = True
            self.reminder_thread = threading.Thread(target=self._check_reminders, daemon=True)
            self.reminder_thread.start()
            logger.info("Reminder controller started")
    
    def stop(self):
        """Stop the reminder checking thread"""
        self.running = False
        if self.reminder_thread:
            self.reminder_thread.join(timeout=5)
        logger.info("Reminder controller stopped")
    
    def _check_reminders(self):
        
        while self.running:
            try:
                current_time = datetime.now()
                notes = self.note_controller.get_all_notes()
                
                for note in notes:
                    reminders = note.get('reminders', [])
                    
                    for idx, reminder in enumerate(reminders):
                        # Create unique identifier for this reminder
                        reminder_id = f"{note['_id']}_{idx}"
                        
                        # Skip if already notified
                        if reminder_id in self.notified_reminders:
                            continue
                        
                        reminder_time = reminder.get('time')
                        if not reminder_time:
                            continue
                        
                        # Convert string to datetime if needed
                        if isinstance(reminder_time, str):
                            try:
                                reminder_time = datetime.fromisoformat(reminder_time)
                            except:
                                continue
                        
                        snoozed_until = reminder.get('snoozed_until')
                        
                        # Skip if snoozed
                        if snoozed_until:
                            if isinstance(snoozed_until, str):
                                try:
                                    snoozed_until = datetime.fromisoformat(snoozed_until)
                                except:
                                    snoozed_until = None
                            
                            if snoozed_until and current_time < snoozed_until:
                                continue
                        
                        # Check if reminder is due (within 1 minute window)
                        time_diff = (reminder_time - current_time).total_seconds()
                        
                        if -60 <= time_diff <= 60:  # Within 1 minute
                            self._send_notification(note, reminder)
                            self.notified_reminders.add(reminder_id)
                            
                            # Handle recurring
                            recurring = reminder.get('recurring')
                            if recurring:
                                next_time = self._calculate_next_reminder(reminder_time, recurring)
                                reminder['time'] = next_time
                                reminder['snoozed_until'] = None
                                
                                # Update note
                                self.note_controller.update_note(
                                    note['_id'],
                                    reminders=reminders
                                )
                                
                                # Remove from notified set so it can trigger again
                                self.notified_reminders.discard(reminder_id)
                            else:
                                # Remove non-recurring reminder
                                self.note_controller.remove_reminder(note['_id'], idx)
                
                # Clean up old notified reminders (older than 24 hours)
                self._cleanup_notified_reminders()
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error checking reminders: {str(e)}")
                time.sleep(self.check_interval)
    
    def _send_notification(self, note: Dict, reminder: Dict):
        """Send a notification"""
        try:
            title = f"📝 Reminder: {note['title']}"
            content = note.get('content', '')
            
            # Truncate content if too long
            if len(content) > 100:
                content = content[:100] + "..."
            
            message = content if content else "Time for your note!"
            
            notification.notify(
                title=title,
                message=message,
                app_name="NoteApp",
                timeout=10
            )
            
            logger.info(f"Notification sent for note: {note['_id']}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
    
    def _calculate_next_reminder(self, current_time: datetime, recurring: str) -> datetime:
      
        if recurring == 'daily':
            return current_time + timedelta(days=1)
        elif recurring == 'weekly':
            return current_time + timedelta(weeks=1)
        elif recurring == 'monthly':
            # Approximate month as 30 days
            return current_time + timedelta(days=30)
        elif recurring == 'weekdays':
            # Next weekday (Monday-Friday)
            next_time = current_time + timedelta(days=1)
            while next_time.weekday() >= 5:  # Skip Saturday (5) and Sunday (6)
                next_time += timedelta(days=1)
            return next_time
        else:
            return current_time
    
    def _cleanup_notified_reminders(self):
        """Clean up old notified reminders"""
        # Keep only the last 1000 notifications
        if len(self.notified_reminders) > 1000:
            # Convert to list, keep last 500
            notified_list = list(self.notified_reminders)
            self.notified_reminders = set(notified_list[-500:])
    
    def snooze_reminder(self, note_id: str, reminder_index: int, snooze_minutes: int = 10) -> bool:
        """Snooze a reminder for specified minutes"""
        try:
            note = self.note_controller.get_note(note_id)
            if not note:
                return False
            
            reminders = note.get('reminders', [])
            if 0 <= reminder_index < len(reminders):
                snooze_until = datetime.now() + timedelta(minutes=snooze_minutes)
                reminders[reminder_index]['snoozed_until'] = snooze_until
                
                # Remove from notified set so it can trigger again
                reminder_id = f"{note_id}_{reminder_index}"
                self.notified_reminders.discard(reminder_id)
                
                return self.note_controller.update_note(note_id, reminders=reminders)
            
            return False
            
        except Exception as e:
            logger.error(f"Error snoozing reminder: {str(e)}")
            return False
    
    def get_upcoming_reminders(self, days_ahead: int = 7) -> List[Dict]:
        """Get all upcoming reminders within specified days"""
        try:
            upcoming = []
            current_time = datetime.now()
            end_time = current_time + timedelta(days=days_ahead)
            
            notes = self.note_controller.get_all_notes()
            
            for note in notes:
                reminders = note.get('reminders', [])
                
                for idx, reminder in enumerate(reminders):
                    reminder_time = reminder.get('time')
                    
                    if not reminder_time:
                        continue
                    
                    # Convert string to datetime if needed
                    if isinstance(reminder_time, str):
                        try:
                            reminder_time = datetime.fromisoformat(reminder_time)
                        except:
                            continue
                    
                    # Check if within time range
                    if current_time <= reminder_time <= end_time:
                        upcoming.append({
                            'note_id': note['_id'],
                            'note_title': note.get('title'),
                            'reminder_index': idx,
                            'reminder_time': reminder_time,
                            'recurring': reminder.get('recurring'),
                            'snoozed_until': reminder.get('snoozed_until')
                        })
            
            # Sort by reminder time
            upcoming.sort(key=lambda x: x['reminder_time'])
            
            return upcoming
            
        except Exception as e:
            logger.error(f"Error getting upcoming reminders: {str(e)}")
            return []
    
    def get_overdue_reminders(self) -> List[Dict]:
        """Get all overdue reminders"""
        try:
            overdue = []
            current_time = datetime.now()
            
            notes = self.note_controller.get_all_notes()
            
            for note in notes:
                reminders = note.get('reminders', [])
                
                for idx, reminder in enumerate(reminders):
                    reminder_time = reminder.get('time')
                    
                    if not reminder_time:
                        continue
                    
                    # Convert string to datetime if needed
                    if isinstance(reminder_time, str):
                        try:
                            reminder_time = datetime.fromisoformat(reminder_time)
                        except:
                            continue
                    
                    # Check if overdue
                    if reminder_time < current_time:
                        # Check if snoozed
                        snoozed_until = reminder.get('snoozed_until')
                        if snoozed_until:
                            if isinstance(snoozed_until, str):
                                try:
                                    snoozed_until = datetime.fromisoformat(snoozed_until)
                                except:
                                    snoozed_until = None
                            
                            if snoozed_until and current_time < snoozed_until:
                                continue
                        
                        overdue.append({
                            'note_id': note['_id'],
                            'note_title': note.get('title'),
                            'reminder_index': idx,
                            'reminder_time': reminder_time,
                            'recurring': reminder.get('recurring')
                        })
            
            return overdue
            
        except Exception as e:
            logger.error(f"Error getting overdue reminders: {str(e)}")
            return []
    
    def clear_all_reminders(self, note_id: str) -> bool:
        """Clear all reminders for a note"""
        try:
            return self.note_controller.update_note(note_id, reminders=[])
        except Exception as e:
            logger.error(f"Error clearing reminders: {str(e)}")
            return False