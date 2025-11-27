"""
Note controller for handling business logic
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from app.models.note_model import NoteModel
from app.models.attachment_model import AttachmentModel

logger = logging.getLogger(__name__)


class NoteController:
    """Controller for Note operations"""
    
    def __init__(self):
        self.note_model = NoteModel()
        self.attachment_model = AttachmentModel()
    
    def create_note(self, title: str, content: str = '', **kwargs) -> Optional[str]:
        """Create a new note with validation"""
        try:
            # Validate title
            if not title or not title.strip():
                logger.error("Title cannot be empty")
                return None
            
            # Prepare note data
            note_data = {
                'title': title.strip(),
                'content': content.strip(),
                'category': kwargs.get('category', 'General'),
                'tags': kwargs.get('tags', []),
                'priority': kwargs.get('priority', 'medium'),
                'due_date': kwargs.get('due_date'),
                'reminders': kwargs.get('reminders', []),
                'color_code': kwargs.get('color_code', '#FFFFFF')
            }
            
            # Validate priority
            valid_priorities = ['low', 'medium', 'high', 'urgent']
            if note_data['priority'] not in valid_priorities:
                note_data['priority'] = 'medium'
            
            # Create note
            note_id = self.note_model.create_note(note_data)
            
            if note_id:
                logger.info(f"Note created successfully: {note_id}")
            
            return note_id
            
        except Exception as e:
            logger.error(f"Error in create_note: {str(e)}")
            return None
    
    def get_note(self, note_id: str) -> Optional[Dict]:
        """Get a note with its attachments"""
        try:
            note = self.note_model.get_note(note_id)
            
            if note:
                # Get attachments
                attachments = self.attachment_model.get_note_attachments(note_id)
                note['attachment_list'] = attachments
            
            return note
            
        except Exception as e:
            logger.error(f"Error in get_note: {str(e)}")
            return None
    
    def update_note(self, note_id: str, **kwargs) -> bool:
        """Update a note"""
        try:
            # Filter out None values
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                return False
            
            return self.note_model.update_note(note_id, update_data)
            
        except Exception as e:
            logger.error(f"Error in update_note: {str(e)}")
            return False
    
    def delete_note(self, note_id: str, delete_attachments: bool = True) -> bool:
        """Delete a note and optionally its attachments"""
        try:
            # Delete attachments first
            if delete_attachments:
                self.attachment_model.delete_note_attachments(note_id)
            
            # Delete note
            return self.note_model.delete_note(note_id)
            
        except Exception as e:
            logger.error(f"Error in delete_note: {str(e)}")
            return False
    
    def get_all_notes(self, include_archived: bool = False, 
                     sort_by: str = 'created_date', ascending: bool = False) -> List[Dict]:
        """Get all notes with sorting"""
        try:
            filters = {}
            if not include_archived:
                filters['is_archived'] = False
            
            return self.note_model.get_all_notes(filters, sort_by, ascending)
            
        except Exception as e:
            logger.error(f"Error in get_all_notes: {str(e)}")
            return []
    
    def search_notes(self, search_term: str, **filters) -> List[Dict]:
        """Search notes with advanced filters"""
        try:
            # Build filter dict
            filter_dict = {}
            
            if 'category' in filters and filters['category']:
                filter_dict['category'] = filters['category']
            
            if 'priority' in filters and filters['priority']:
                filter_dict['priority'] = filters['priority']
            
            if 'is_starred' in filters:
                filter_dict['is_starred'] = filters['is_starred']
            
            if 'tags' in filters and filters['tags']:
                filter_dict['tags'] = {'$in': filters['tags']}
            
            # Date range filter
            if 'date_from' in filters or 'date_to' in filters:
                date_filter = {}
                if 'date_from' in filters:
                    date_filter['$gte'] = filters['date_from']
                if 'date_to' in filters:
                    date_filter['$lte'] = filters['date_to']
                filter_dict['created_date'] = date_filter
            
            return self.note_model.search_notes(search_term, filter_dict)
            
        except Exception as e:
            logger.error(f"Error in search_notes: {str(e)}")
            return []
    
    def toggle_star(self, note_id: str) -> bool:
        """Toggle star status"""
        return self.note_model.toggle_star(note_id)
    
    def toggle_archive(self, note_id: str) -> bool:
        """Toggle archive status"""
        return self.note_model.toggle_archive(note_id)
    
    def add_reminder(self, note_id: str, reminder_time: datetime, 
                    recurring: str = None) -> bool:
        """Add a reminder to a note"""
        try:
            # Validate reminder time
            if reminder_time <= datetime.now():
                logger.error("Reminder time must be in the future")
                return False
            
            reminder = {
                'time': reminder_time,
                'recurring': recurring,
                'snoozed_until': None
            }
            
            note = self.note_model.get_note(note_id)
            if not note:
                return False
            
            reminders = note.get('reminders', [])
            reminders.append(reminder)
            
            return self.note_model.update_note(note_id, {'reminders': reminders})
            
        except Exception as e:
            logger.error(f"Error in add_reminder: {str(e)}")
            return False
    
    def remove_reminder(self, note_id: str, reminder_index: int) -> bool:
        """Remove a specific reminder"""
        try:
            note = self.note_model.get_note(note_id)
            if not note:
                return False
            
            reminders = note.get('reminders', [])
            if 0 <= reminder_index < len(reminders):
                reminders.pop(reminder_index)
                return self.note_model.update_note(note_id, {'reminders': reminders})
            
            return False
            
        except Exception as e:
            logger.error(f"Error in remove_reminder: {str(e)}")
            return False
    
    def snooze_reminder(self, note_id: str, reminder_index: int, 
                       snooze_minutes: int) -> bool:
        """Snooze a reminder"""
        try:
            note = self.note_model.get_note(note_id)
            if not note:
                return False
            
            reminders = note.get('reminders', [])
            if 0 <= reminder_index < len(reminders):
                snooze_until = datetime.now() + timedelta(minutes=snooze_minutes)
                reminders[reminder_index]['snoozed_until'] = snooze_until
                return self.note_model.update_note(note_id, {'reminders': reminders})
            
            return False
            
        except Exception as e:
            logger.error(f"Error in snooze_reminder: {str(e)}")
            return False
    
    def add_attachment(self, note_id: str, file_path: str, filename: str = None) -> Optional[str]:
        """Add an attachment to a note"""
        return self.attachment_model.add_attachment(note_id, file_path, filename)
    
    def get_attachments(self, note_id: str) -> List[Dict]:
        """Get all attachments for a note"""
        return self.attachment_model.get_note_attachments(note_id)
    
    def delete_attachment(self, attachment_id: str) -> bool:
        """Delete an attachment"""
        return self.attachment_model.delete_attachment(attachment_id)
    
    def bulk_delete_notes(self, note_ids: List[str]) -> int:
        """Delete multiple notes"""
        return self.note_model.bulk_delete(note_ids)
    
    def bulk_move_category(self, note_ids: List[str], category: str) -> int:
        """Move multiple notes to a category"""
        return self.note_model.bulk_update_category(note_ids, category)
    
    def get_statistics(self) -> Dict:
        """Get note statistics"""
        try:
            all_notes = self.note_model.get_all_notes()
            
            stats = {
                'total_notes': len(all_notes),
                'starred': len([n for n in all_notes if n.get('is_starred')]),
                'archived': len([n for n in all_notes if n.get('is_archived')]),
                'by_priority': {
                    'urgent': len([n for n in all_notes if n.get('priority') == 'urgent']),
                    'high': len([n for n in all_notes if n.get('priority') == 'high']),
                    'medium': len([n for n in all_notes if n.get('priority') == 'medium']),
                    'low': len([n for n in all_notes if n.get('priority') == 'low'])
                },
                'by_category': {},
                'total_words': sum(n.get('word_count', 0) for n in all_notes),
                'due_this_week': len(self.note_model.get_due_notes(7))
            }
            
            # Count by category
            categories = self.note_model.get_categories()
            for cat in categories:
                stats['by_category'][cat] = len([n for n in all_notes if n.get('category') == cat])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def export_note(self, note_id: str, format: str = 'txt') -> Optional[str]:
        """Export note to file"""
        try:
            note = self.get_note(note_id)
            if not note:
                return None
            
            export_dir = os.path.join('app', 'assets', 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{note['title']}_{timestamp}"
            
            if format == 'txt':
                filepath = os.path.join(export_dir, f"{filename}.txt")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {note['title']}\n")
                    f.write(f"Category: {note.get('category', 'N/A')}\n")
                    f.write(f"Created: {note.get('created_date')}\n")
                    f.write(f"Tags: {', '.join(note.get('tags', []))}\n\n")
                    f.write(note.get('content', ''))
            
            elif format == 'md':
                filepath = os.path.join(export_dir, f"{filename}.md")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# {note['title']}\n\n")
                    f.write(f"**Category:** {note.get('category', 'N/A')}  \n")
                    f.write(f"**Created:** {note.get('created_date')}  \n")
                    f.write(f"**Tags:** {', '.join(note.get('tags', []))}  \n\n")
                    f.write(note.get('content', ''))
            
            else:
                logger.error(f"Unsupported export format: {format}")
                return None
            
            logger.info(f"Note exported: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting note: {str(e)}")
            return None


import os