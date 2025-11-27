
import re
from datetime import datetime, timedelta
import hashlib
from cryptography.fernet import Fernet
import os
import json
from typing import Any, Dict, List


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def format_date(date: datetime, format: str = "%Y-%m-%d %H:%M") -> str:
    """Format datetime object to string"""
    if not date:
        return "N/A"
    
    if isinstance(date, str):
        try:
            date = datetime.fromisoformat(date)
        except:
            return date
    
    return date.strftime(format)


def format_relative_time(date: datetime) -> str:
    """Format datetime as relative time (e.g., '2 hours ago')"""
    if isinstance(date, str):
        try:
            date = datetime.fromisoformat(date)
        except:
            return date
    
    now = datetime.now()
    diff = now - date
    
    if diff.total_seconds() < 60:
        return "just now"
    elif diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.days == 1:
        return "yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif diff.days < 365:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"


def parse_date(date_str: str, format: str = "%Y-%m-%d %H:%M") -> datetime:
    """Parse string to datetime object"""
    try:
        return datetime.strptime(date_str, format)
    except:
        return None


def parse_smart_date(date_str: str) -> datetime:
    """Parse smart date strings like 'tomorrow', 'next week', etc."""
    date_str = date_str.lower().strip()
    now = datetime.now()
    
    if date_str in ['today', 'now']:
        return now
    elif date_str == 'tomorrow':
        return now + timedelta(days=1)
    elif date_str == 'yesterday':
        return now - timedelta(days=1)
    elif date_str == 'next week':
        return now + timedelta(weeks=1)
    elif date_str == 'next month':
        return now + timedelta(days=30)
    elif date_str.startswith('in '):
        # Parse "in X days/weeks/months"
        parts = date_str.split()
        if len(parts) >= 3:
            try:
                amount = int(parts[1])
                unit = parts[2].lower()
                
                if 'day' in unit:
                    return now + timedelta(days=amount)
                elif 'week' in unit:
                    return now + timedelta(weeks=amount)
                elif 'month' in unit:
                    return now + timedelta(days=amount * 30)
                elif 'hour' in unit:
                    return now + timedelta(hours=amount)
            except:
                pass
    
    # Try standard parsing
    try:
        return datetime.fromisoformat(date_str)
    except:
        return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def get_file_size_readable(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def generate_hash(text: str) -> str:
    """Generate SHA256 hash"""
    return hashlib.sha256(text.encode()).hexdigest()


def generate_pin_hash(pin: str) -> str:
    """Generate hash for PIN with salt"""
    salt = os.getenv('ENCRYPTION_KEY', 'default-salt')
    combined = f"{pin}{salt}"
    return hashlib.sha256(combined.encode()).hexdigest()


def verify_pin(pin: str, pin_hash: str) -> bool:
    """Verify PIN against hash"""
    return generate_pin_hash(pin) == pin_hash


def encrypt_data(data: str, key: bytes = None) -> str:
    """Encrypt data using Fernet"""
    try:
        if key is None:
            key_string = os.getenv('ENCRYPTION_KEY', 'default-key-32-characters-long!')
            # Ensure key is 32 bytes for Fernet
            key = hashlib.sha256(key_string.encode()).digest()
            key = Fernet.generate_key()  # Generate proper key
        
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data.encode())
        return encrypted.decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return data


def decrypt_data(encrypted_data: str, key: bytes = None) -> str:
    """Decrypt data using Fernet"""
    try:
        if key is None:
            key_string = os.getenv('ENCRYPTION_KEY', 'default-key-32-characters-long!')
            key = hashlib.sha256(key_string.encode()).digest()
            key = Fernet.generate_key()  # Generate proper key
        
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return encrypted_data


def extract_tags(text: str) -> List[str]:
    """Extract hashtags from text"""
    tags = re.findall(r'#(\w+)', text)
    return list(set(tags))  # Remove duplicates


def highlight_text(text: str, search_term: str, tag: str = "**") -> str:
    """Highlight search term in text (for display)"""
    if not search_term or not text:
        return text
    
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    return pattern.sub(lambda m: f"{tag}{m.group()}{tag}", text)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    # Remove invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Limit length
    max_length = 255
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        name = name[:max_length - len(ext)]
        sanitized = name + ext
    
    return sanitized


def calculate_word_count(text: str) -> int:
    """Calculate word count of text"""
    if not text:
        return 0
    
    words = text.split()
    return len(words)


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time in minutes"""
    word_count = calculate_word_count(text)
    minutes = word_count / words_per_minute
    return max(1, int(minutes))  # Minimum 1 minute


def export_to_json(data: Any, filepath: str) -> bool:
    """Export data to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Export error: {e}")
        return False


def import_from_json(filepath: str) -> Any:
    """Import data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Import error: {e}")
        return None


def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file type against allowed extensions"""
    if not filename:
        return False
    
    ext = os.path.splitext(filename)[1].lower().replace('.', '')
    return ext in [e.lower() for e in allowed_extensions]


def validate_file_size(filepath: str, max_size_mb: int = 10) -> bool:
    """Validate file size"""
    try:
        size_bytes = os.path.getsize(filepath)
        size_mb = size_bytes / (1024 * 1024)
        return size_mb <= max_size_mb
    except:
        return False


def create_backup_filename(prefix: str = "backup") -> str:
    """Create a timestamped backup filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.json"


def search_text(text: str, search_term: str, case_sensitive: bool = False) -> bool:
    """Check if text contains search term"""
    if not search_term:
        return True
    
    if not text:
        return False
    
    if not case_sensitive:
        text = text.lower()
        search_term = search_term.lower()
    
    return search_term in text


def fuzzy_search(text: str, search_term: str, threshold: float = 0.6) -> bool:
    """Fuzzy search using simple character matching"""
    if not search_term or not text:
        return False
    
    text = text.lower()
    search_term = search_term.lower()
    
    # Simple fuzzy matching based on character presence
    matches = sum(1 for char in search_term if char in text)
    ratio = matches / len(search_term)
    
    return ratio >= threshold


def color_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_color(rgb: tuple) -> str:
    """Convert RGB tuple to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def get_contrast_color(hex_color: str) -> str:
    """Get contrasting color (black or white) for a given color"""
    rgb = color_to_rgb(hex_color)
    # Calculate luminance
    luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
    
    return "#000000" if luminance > 0.5 else "#FFFFFF"


def format_tags_display(tags: List[str], max_display: int = 5) -> str:
    """Format tags for display"""
    if not tags:
        return "No tags"
    
    display_tags = tags[:max_display]
    formatted = ", ".join([f"#{tag}" for tag in display_tags])
    
    if len(tags) > max_display:
        formatted += f" +{len(tags) - max_display} more"
    
    return formatted


def parse_boolean(value: Any) -> bool:
    """Parse various boolean representations"""
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value = value.lower()
        return value in ['true', '1', 'yes', 'on', 'enabled']
    
    if isinstance(value, int):
        return value != 0
    
    return bool(value)


def get_priority_color(priority: str) -> str:
    """Get color code for priority level"""
    colors = {
        'urgent': '#DC2626',
        'high': '#EA580C',
        'medium': '#CA8A04',
        'low': '#16A34A'
    }
    return colors.get(priority.lower(), '#6B7280')


def get_priority_emoji(priority: str) -> str:
    """Get emoji for priority level"""
    emojis = {
        'urgent': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢'
    }
    return emojis.get(priority.lower(), '⚪')