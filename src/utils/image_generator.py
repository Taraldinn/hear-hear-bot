"""
Image generation utilities for feedback and ballots
Author: Tasdid Tahsin
Email: tasdidtahsin@gmail.com
"""

from PIL import Image, ImageFont, ImageDraw
import io
import os
from pathlib import Path

class ImageGenerator:
    """Generates images for feedback and ballot displays"""
    
    def __init__(self):
        self.assets_path = Path(__file__).parent.parent.parent / "assets"
        self.fonts_path = self.assets_path / "fonts" / "segoe ui"
        
    def get_font(self, size=20, bold=False, italic=False):
        """Get font with specified properties"""
        font_name = "regular.ttf"
        
        if bold and italic:
            font_name = "bolditalic.ttf"
        elif bold:
            font_name = "bold.ttf"
        elif italic:
            font_name = "italic.ttf"
        
        font_path = self.fonts_path / font_name
        
        try:
            return ImageFont.truetype(str(font_path), size)
        except (OSError, IOError):
            # Fallback to default font
            return ImageFont.load_default()
    
    def create_feedback_image(self, round_name, oralist_name, score, feedback_text=""):
        """Create a feedback image"""
        # Create base image
        width, height = 800, 600
        background_color = (255, 255, 255)  # White
        
        img = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(img)
        
        # Load background template if available
        bg_path = self.assets_path / "feedback.png"
        if bg_path.exists():
            try:
                bg_img = Image.open(bg_path)
                bg_img = bg_img.resize((width, height))
                img.paste(bg_img, (0, 0))
                draw = ImageDraw.Draw(img)
            except Exception:
                pass  # Use plain background
        
        # Colors
        title_color = (33, 37, 41)
        text_color = (52, 58, 64)
        score_color = (220, 53, 69) if float(score) < 70 else (40, 167, 69)
        
        # Fonts
        title_font = self.get_font(36, bold=True)
        subtitle_font = self.get_font(24, bold=True)
        text_font = self.get_font(18)
        score_font = self.get_font(48, bold=True)
        
        # Draw title
        title = "DEBATE FEEDBACK"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 30), title, fill=title_color, font=title_font)
        
        # Draw round
        round_text = f"Round: {round_name}"
        draw.text((50, 100), round_text, fill=text_color, font=subtitle_font)
        
        # Draw oralist name
        oralist_text = f"Speaker: {oralist_name}"
        draw.text((50, 140), oralist_text, fill=text_color, font=subtitle_font)
        
        # Draw score
        score_text = f"Score: {score}"
        score_bbox = draw.textbbox((0, 0), score_text, font=score_font)
        score_width = score_bbox[2] - score_bbox[0]
        score_x = (width - score_width) // 2
        draw.text((score_x, 200), score_text, fill=score_color, font=score_font)
        
        # Draw feedback text if provided
        if feedback_text:
            feedback_y = 300
            max_width = width - 100
            lines = self._wrap_text(feedback_text, text_font, max_width)
            
            for line in lines:
                draw.text((50, feedback_y), line, fill=text_color, font=text_font)
                feedback_y += 25
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    def create_ballot_image(self, motion, teams_data, judges_data=None):
        """Create a ballot results image"""
        width, height = 1000, 800
        background_color = (255, 255, 255)
        
        img = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(img)
        
        # Load ballot background if available
        bg_path = self.assets_path / "ballot.png"
        if bg_path.exists():
            try:
                bg_img = Image.open(bg_path)
                bg_img = bg_img.resize((width, height))
                img.paste(bg_img, (0, 0))
                draw = ImageDraw.Draw(img)
            except Exception:
                pass
        
        # Colors
        title_color = (33, 37, 41)
        text_color = (52, 58, 64)
        accent_color = (0, 123, 255)
        
        # Fonts
        title_font = self.get_font(28, bold=True)
        subtitle_font = self.get_font(20, bold=True)
        text_font = self.get_font(16)
        
        # Draw title
        title = "BALLOT RESULTS"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 30), title, fill=title_color, font=title_font)
        
        # Draw motion (wrapped)
        motion_lines = self._wrap_text(f"Motion: {motion}", text_font, width - 100)
        y_pos = 80
        for line in motion_lines:
            draw.text((50, y_pos), line, fill=text_color, font=text_font)
            y_pos += 22
        
        # Draw teams data
        y_pos += 30
        if teams_data:
            draw.text((50, y_pos), "TEAMS:", fill=accent_color, font=subtitle_font)
            y_pos += 30
            
            for team_data in teams_data:
                team_line = f"• {team_data}"
                draw.text((70, y_pos), team_line, fill=text_color, font=text_font)
                y_pos += 22
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Word is too long, add it anyway
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

# Global image generator instance
image_generator = ImageGenerator()
