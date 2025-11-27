"""
Attachment model for managing file attachments
"""
import os
import shutil
from datetime import datetime
from bson import ObjectId
from typing import List, Dict, Optional
import logging
from PIL import Image

from .database import db_instance

logger = logging.getLogger(__name__)


class AttachmentModel:
    """Model for Attachment operations"""
    
    def __init__(self):
        self.db = db_instance.get_database()
        self.collection = self.db.attachments
        self.upload_dir = os.path.join('app', 'assets', 'uploads')
        self.thumbnail_dir = os.path.join(self.upload_dir, 'thumbnails')
        
        # Create directories if they don't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.thumbnail_dir, exist_ok=True)
    
    def add_attachment(self, note_id: str, file_path: str, filename: str = None) -> Optional[str]:
        """Add an attachment to a note"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
            
            # Get file info
            if filename is None:
                filename = os.path.basename(file_path)
            
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Check file size limit (10MB default)
            max_size = int(os.getenv('MAX_FILE_SIZE', 10485760))
            if file_size > max_size:
                logger.error(f"File too large: {file_size} bytes")
                return None
            
            # Check allowed extensions
            allowed_exts = os.getenv('ALLOWED_EXTENSIONS', 'pdf,docx,xlsx,jpg,jpeg,png,gif').split(',')
            if file_ext.replace('.', '') not in allowed_exts:
                logger.error(f"File type not allowed: {file_ext}")
                return None
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            destination = os.path.join(self.upload_dir, unique_filename)
            
            # Copy file
            shutil.copy2(file_path, destination)
            
            # Create thumbnail for images
            thumbnail_path = None
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                thumbnail_path = self._create_thumbnail(destination, unique_filename)
            
            # Create attachment record
            attachment = {
                'note_id': note_id,
                'filename': filename,
                'unique_filename': unique_filename,
                'filepath': destination,
                'filetype': file_ext,
                'filesize': file_size,
                'thumbnail': thumbnail_path,
                'upload_date': datetime.now()
            }
            
            result = self.collection.insert_one(attachment)
            logger.info(f"Attachment added: {result.inserted_id}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error adding attachment: {str(e)}")
            return None
    
    def get_attachment(self, attachment_id: str) -> Optional[Dict]:
        """Get an attachment by ID"""
        try:
            attachment = self.collection.find_one({'_id': ObjectId(attachment_id)})
            if attachment:
                attachment['_id'] = str(attachment['_id'])
            return attachment
        except Exception as e:
            logger.error(f"Error getting attachment: {str(e)}")
            return None
    
    def get_note_attachments(self, note_id: str) -> List[Dict]:
        """Get all attachments for a note"""
        try:
            attachments = list(self.collection.find({'note_id': note_id}))
            
            for attachment in attachments:
                attachment['_id'] = str(attachment['_id'])
            
            return attachments
            
        except Exception as e:
            logger.error(f"Error getting note attachments: {str(e)}")
            return []
    
    def delete_attachment(self, attachment_id: str) -> bool:
        """Delete an attachment"""
        try:
            attachment = self.get_attachment(attachment_id)
            if not attachment:
                return False
            
            # Delete files
            if os.path.exists(attachment['filepath']):
                os.remove(attachment['filepath'])
            
            if attachment.get('thumbnail') and os.path.exists(attachment['thumbnail']):
                os.remove(attachment['thumbnail'])
            
            # Delete record
            result = self.collection.delete_one({'_id': ObjectId(attachment_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Attachment deleted: {attachment_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting attachment: {str(e)}")
            return False
    
    def delete_note_attachments(self, note_id: str) -> int:
        """Delete all attachments for a note"""
        try:
            attachments = self.get_note_attachments(note_id)
            deleted_count = 0
            
            for attachment in attachments:
                if self.delete_attachment(attachment['_id']):
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting note attachments: {str(e)}")
            return 0
    
    def _create_thumbnail(self, image_path: str, filename: str) -> Optional[str]:
        """Create a thumbnail for an image"""
        try:
            thumbnail_size = (200, 200)
            
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                
                # Save thumbnail
                thumbnail_filename = f"thumb_{filename}"
                thumbnail_path = os.path.join(self.thumbnail_dir, thumbnail_filename)
                img.save(thumbnail_path, 'JPEG', quality=85)
                
                return thumbnail_path
                
        except Exception as e:
            logger.error(f"Error creating thumbnail: {str(e)}")
            return None
    
    def get_total_size(self, note_id: str = None) -> int:
        """Get total size of attachments"""
        try:
            query = {'note_id': note_id} if note_id else {}
            attachments = self.collection.find(query)
            
            total_size = sum(att.get('filesize', 0) for att in attachments)
            return total_size
            
        except Exception as e:
            logger.error(f"Error getting total size: {str(e)}")
            return 0