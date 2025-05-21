from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from textwrap import wrap
from collections import defaultdict

class PDFGenerator:
    def __init__(self, output_file, background_image, logo_path="static/logo/logo.jpeg", qr_code_path="static/logo/qr_code.jpeg"):
        self.output_file = output_file
        self.background_image = background_image
        self.logo_path = logo_path
        self.qr_code_path = qr_code_path
        self.page_width, self.page_height = A4
        self.margin = 50
        self.line_height = 18

    def crea_pdf(self, nome, cognome, data_nascita, posizione, mano_dominante, frasi_per_fase): 
        first_name= nome
        last_name=cognome
        birth_date=data_nascita
        position=posizione
        dominant_hand=mano_dominante
        phrases_by_phase=frasi_per_fase
        c = canvas.Canvas(self.output_file, pagesize=A4)

        def draw_background():
            bg = ImageReader(self.background_image)
            c.drawImage(bg, 0, 0, width=self.page_width, height=self.page_height)

        def draw_logo():
            try:
                logo = ImageReader(self.logo_path)
                c.drawImage(logo, self.margin, self.page_height - 100, width=80, height=80, mask='auto')
            except Exception as e:
                print(f"Error loading logo: {e}")

        def draw_qr_code():
            if not self.qr_code_path:
                return
            try:
                qr = ImageReader(self.qr_code_path)
                qr_width = 80
                qr_height = 80
                x_pos = self.page_width - self.margin - qr_width
                y_pos = self.page_height - self.margin - 50
                c.drawImage(qr, x_pos, y_pos, width=qr_width, height=qr_height, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                print(f"Errore caricamento QR code: {e}")


        def write_wrapped_text(x, y, text, font="Helvetica", size=16, max_width=90):
            c.setFont(font, size)
            c.setFillColorRGB(1, 1, 1)
            lines = wrap(text, width=max_width)
            for line in lines:
                if y < self.margin:
                    c.showPage()
                    draw_background()
                    draw_logo()
                    c.setFont(font, size)
                    c.setFillColorRGB(1, 1, 1)
                    y = self.page_height - self.margin
                c.drawString(x, y, line)
                y -= self.line_height + 4
            return y

        def draw_line(y_pos):
            c.setStrokeColorRGB(1, 1, 1)
            c.setLineWidth(1)
            c.line(self.margin, y_pos, self.page_width - self.margin, y_pos)

        def draw_two_column_info(x, y, info_left, info_right):
            spacing = 250
            for left, right in zip(info_left, info_right):
                y_left = write_wrapped_text(x, y, left, size=15, max_width=40)
                y_right = write_wrapped_text(x + spacing, y, right, size=15, max_width=40)
                y = min(y_left, y_right)
            return y

        def draw_image_with_aspect(image_path, x, y_top, max_width, max_height):
            try:
                img = ImageReader(image_path)
                iw, ih = img.getSize()
                aspect = ih / iw
                width = max_width
                height = width * aspect
                if height > max_height:
                    height = max_height
                    width = height / aspect
                x_centered = (self.page_width - width) / 2
                y_centered = y_top - height
                c.drawImage(img, x_centered, y_centered, width=width, height=height, preserveAspectRatio=True, mask='auto')
                return height
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
                return 0

        def draw_footer():
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(1, 1, 1)
            c.drawString(self.margin, 20, "Contact us: Wizshotai@gmail.com")
            c.drawString(self.page_width - 150, 20, "2025 © WizShotAi")

        def draw_phase_block(title, image_path, phrases, y_start):
            c.setFont("Helvetica-Bold", 20)
            c.setFillColorRGB(1, 1, 1)
            title_width = c.stringWidth(title, "Helvetica-Bold", 20)
            c.drawString((self.page_width - title_width) / 2, y_start, title.upper())
            y = y_start - 25
            image_height = draw_image_with_aspect(image_path, self.margin, y, 400, 300)
            y -= image_height + 10
            draw_line(y)
            y -= 20
            for phrase in phrases:
                if y < self.margin:
                    c.showPage()
                    draw_background()
                    draw_logo()
                    c.setFont("Helvetica-Bold", 20)
                    c.drawString((self.page_width - title_width) / 2, self.page_height - self.margin - 30, title.upper())
                    y = self.page_height - self.margin - 60
                y = write_wrapped_text(self.margin, y, f"- {phrase}", size=16, max_width=70)
            return y

        def draw_phase_page(title, image_path, phrases):
            c.showPage()
            draw_background()
            draw_qr_code()
            draw_logo()
            y_start = self.page_height - self.margin - 60
            draw_phase_block(title, image_path, phrases, y_start)
            draw_footer()

        # Prima pagina
        draw_background()
        draw_qr_code()
        draw_logo()
        y = self.page_height - self.margin - 90
        c.setFont("Helvetica-Bold", 20)
        y = write_wrapped_text(self.margin, y, "Player Information:", font="Helvetica-Bold", size=20)
        info_left = [f"First Name: {first_name}", f"Date of Birth: {birth_date}"]
        info_right = [f"Last Name: {last_name}", f"Position: {position}"]
        y -= 10
        y = draw_two_column_info(self.margin, y, info_left, info_right)
        y -= 30

        # Mappa fase -> immagine
        image_map = {
            "preparation": "static/temp_frames/preparazione.jpg",
            "transition": "static/temp_frames/estensione.jpg",
            "release": "static/temp_frames/rilascio.jpg",
            "follow-through": "static/temp_frames/Follow-Through.jpg"
        }

        # Prima pagina: preparation
        prep_phrases = phrases_by_phase.get("preparation", [])
        y = draw_phase_block("Preparation", image_map["preparation"], prep_phrases, y)
        draw_footer()

        # Altre fasi
        for phase in ["transition", "release", "follow-through"]:
            draw_phase_page(phase.capitalize(), image_map[phase], phrases_by_phase.get(phase, []))

        c.save()
        print(f"✅ PDF created: {self.output_file}")

    def raggruppa_frasi_per_fase(self, flat_phrase_list):
        phases = {
            "preparation": "preparation",
            "transition": "transition",
            "release": "release",
            "follow-through": "follow-through"
        }
        grouped = defaultdict(list)
        for phrase in flat_phrase_list:
            phrase_lower = phrase.lower()
            for keyword, phase_key in phases.items():
                if keyword in phrase_lower:
                    grouped[phase_key].append(phrase)
                    break
        return grouped
