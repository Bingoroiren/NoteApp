"""
Note model for managing note data
"""
from datetime import datetime
from bson import ObjectId
from typing import List, Dict, Optional
import logging

from .database import db_instance

logger = logging.getLogger(__name__)


class NoteModel:
    """Model for Note operations"""
    
    def __init__(self):
        self.db = db_instance.get_database()
        self.collection = self.db.notes
    
    def create_note(self, note_data: Dict) -> Optional[str]:
        """Create a new note"""
        try:
            # Set default values
            note = {
                'title': note_data.get('title', 'Untitled'),
                'content': note_data.get('content', ''),
                'category': note_data.get('category', 'General'),
                'tags': note_data.get('tags', []),
                'priority': note_data.get('priority', 'medium'),
                'created_date': datetime.now(),
                'updated_date': datetime.now(),
                'due_date': note_data.get('due_date'),
                'reminders': note_data.get('reminders', []),
                'is_starred': note_data.get('is_starred', False),
                'is_archived': note_data.get('is_archived', False),
                'is_locked': note_data.get('is_locked', False),
                'attachments': note_data.get('attachments', []),
                'color_code': note_data.get('color_code', '#FFFFFF'),
                'word_count': self._calculate_word_count(note_data.get('content', '')),
                'version_history': [],
                'shared_with': note_data.get('shared_with', []),
                'comments': note_data.get('comments', []),
                'pomodoro_sessions': note_data.get('pomodoro_sessions', 0)
            }
            
            result = self.collection.insert_one(note)
            logger.info(f"Note created with ID: {result.inserted_id}")
            
            # Log to audit
            self._log_audit('create', str(result.inserted_id), note)
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating note: {str(e)}")
            return None
    
    def get_note(self, note_id: str) -> Optional[Dict]:
        """Get a note by ID"""
        try:
            note = self.collection.find_one({'_id': ObjectId(note_id)})
            if note:
                note['_id'] = str(note['_id'])
            return note
        except Exception as e:
            logger.error(f"Error getting note: {str(e)}")
            return None
    
    def update_note(self, note_id: str, update_data: Dict) -> bool:
        """Update a note"""
        try:
            # Get current version for history
            current_note = self.get_note(note_id)
            if not current_note:
                return False
            
            # Add to version history
            version_entry = {
                'timestamp': datetime.now(),
                'content': current_note.get('content'),
                'title': current_note.get('title')
            }
            
            # Prepare update
            update_data['updated_date'] = datetime.now()
            if 'content' in update_data:
                update_data['word_count'] = self._calculate_word_count(update_data['content'])
            
            # Add version to history
            self.collection.update_one(
                {'_id': ObjectId(note_id)},
                {'$push': {'version_history': version_entry}}
            )
            
            # Update note
            result = self.collection.update_one(
                {'_id': ObjectId(note_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Note updated: {note_id}")
                self._log_audit('update', note_id, update_data)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating note: {str(e)}")
            return False
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(note_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Note deleted: {note_id}")
                self._log_audit('delete', note_id, {})
                
                # Delete associated attachments
                self.db.attachments.delete_many({'note_id': note_id})
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting note: {str(e)}")
            return False
    
    def get_all_notes(self, filters: Dict = None, sort_by: str = 'created_date', 
                     ascending: bool = False) -> List[Dict]:
        """Get all notes with optional filters"""
        try:
            query = filters or {}
            sort_order = 1 if ascending else -1
            
            notes = list(self.collection.find(query).sort(sort_by, sort_order))
            
            # Convert ObjectId to string
            for note in notes:
                note['_id'] = str(note['_id'])
            
            return notes
            
        except Exception as e:
            logger.error(f"Error getting notes: {str(e)}")
            return []
    
    def search_notes(self, search_term: str, filters: Dict = None) -> List[Dict]:
        """Search notes by title or content"""
        try:
            query = {
                '$or': [
                    {'title': {'$regex': search_term, '$options': 'i'}},
                    {'content': {'$regex': search_term, '$options': 'i'}},
                    {'tags': {'$regex': search_term, '$options': 'i'}}
                ]
            }
            
            # Add additional filters
            if filters:
                query = {'$and': [query, filters]}
            
            notes = list(self.collection.find(query))
            
            for note in notes:
                note['_id'] = str(note['_id'])
            
            return notes
            
        except Exception as e:
            logger.error(f"Error searching notes: {str(e)}")
            return []
    
    def get_starred_notes(self) -> List[Dict]:
        """Get all starred notes"""
        return self.get_all_notes({'is_starred': True})
    
    def get_archived_notes(self) -> List[Dict]:
        """Get all archived notes"""
        return self.get_all_notes({'is_archived': True})
    
    def get_notes_by_category(self, category: str) -> List[Dict]:
        """Get notes by category"""
        return self.get_all_notes({'category': category})
    
    def get_notes_by_tag(self, tag: str) -> List[Dict]:
        """Get notes by tag"""
        return self.get_all_notes({'tags': tag})
    
    def get_notes_by_priority(self, priority: str) -> List[Dict]:
        """Get notes by priority"""
        return self.get_all_notes({'priority': priority})
    
    def get_due_notes(self, days_ahead: int = 7) -> List[Dict]:
        """Get notes due within specified days"""
        try:
            from datetime import timedelta
            
            end_date = datetime.now() + timedelta(days=days_ahead)
            
            notes = list(self.collection.find({
                'due_date': {
                    '$gte': datetime.now(),
                    '$lte': end_date
                }
            }).sort('due_date', 1))
            
            for note in notes:
                note['_id'] = str(note['_id'])
            
            return notes
            
        except Exception as e:
            logger.error(f"Error getting due notes: {str(e)}")
            return []
    
    def toggle_star(self, note_id: str) -> bool:
        """Toggle star status of a note"""
        try:
            note = self.get_note(note_id)
            if not note:
                return False
            
            new_status = not note.get('is_starred', False)
            return self.update_note(note_id, {'is_starred': new_status})
            
        except Exception as e:
            logger.error(f"Error toggling star: {str(e)}")
            return False
    
    def toggle_archive(self, note_id: str) -> bool:
        """Toggle archive status of a note"""
        try:
            note = self.get_note(note_id)
            if not note:
                return False
            
            new_status = not note.get('is_archived', False)
            return self.update_note(note_id, {'is_archived': new_status})
            
        except Exception as e:
            logger.error(f"Error toggling archive: {str(e)}")
            return False
    
    def bulk_delete(self, note_ids: List[str]) -> int:
        """Delete multiple notes"""
        try:
            object_ids = [ObjectId(nid) for nid in note_ids]
            result = self.collection.delete_many({'_id': {'$in': object_ids}})
            
            logger.info(f"Bulk deleted {result.deleted_count} notes")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error in bulk delete: {str(e)}")
            return 0
    
    def bulk_update_category(self, note_ids: List[str], category: str) -> int:
        """Update category for multiple notes"""
        try:
            object_ids = [ObjectId(nid) for nid in note_ids]
            result = self.collection.update_many(
                {'_id': {'$in': object_ids}},
                {'$set': {'category': category, 'updated_date': datetime.now()}}
            )
            
            return result.modified_count
            
        except Exception as e:
            logger.error(f"Error in bulk update: {str(e)}")
            return 0
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        try:
            categories = self.collection.distinct('category')
            return sorted(categories)
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            return []
    
    def get_tags(self) -> List[str]:
        """Get all unique tags"""
        try:
            # Get all tags from all notes
            all_tags = []
            notes = self.collection.find({}, {'tags': 1})
            
            for note in notes:
                all_tags.extend(note.get('tags', []))
            
            return sorted(list(set(all_tags)))
            
        except Exception as e:
            logger.error(f"Error getting tags: {str(e)}")
            return []
    
    def _calculate_word_count(self, content: str) -> int:
        """Calculate word count of content"""
        return len(content.split())
    
    def _log_audit(self, action: str, note_id: str, data: Dict):
        """Log action to audit trail"""
        try:
            audit_entry = {
                'action': action,
                'note_id': note_id,
                'timestamp': datetime.now(),
                'data': data
            }
            self.db.audit_log.insert_one(audit_entry)
        except Exception as e:
            logger.warning(f"Error logging audit: {str(e)}")