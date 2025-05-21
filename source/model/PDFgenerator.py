from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from textwrap import wrap
from collections import defaultdict

class PDFGenerator:
    def __init__(self, output_file, background_image, logo_path="static/logo/logo.jpeg"):
        self.output_file = output_file
        self.background_image = background_image
        self.logo_path = logo_path
        self.page_width, self.page_height = A4
        self.margin = 50
        self.line_height = 18

    def crea_pdf(self, nome, cognome, data_nascita, posizione, mano_dominante, frasi_per_fase):
        c = canvas.Canvas(self.output_file, pagesize=A4)

        def draw_background():
            bg = ImageReader(self.background_image)
            c.drawImage(bg, 0, 0, width=self.page_width, height=self.page_height)

        def draw_logo():
            try:
                logo = ImageReader(self.logo_path)
                logo_width = 80
                logo_height = 80
                padding_top = 20
                c.drawImage(
                    logo,
                    self.margin,
                    self.page_height - logo_height - padding_top,
                    width=logo_width,
                    height=logo_height,
                    mask='auto'
                )
            except Exception as e:
                print(f"Errore caricando il logo: {e}")

        def write_wrapped_text(x, y, text, font="Helvetica", size=16, max_width=90):
            c.setFont(font, size)
            c.setFillColorRGB(1, 1, 1)  # Testo bianco
            lines = wrap(text, width=max_width)
            for line in lines:
                if y < self.margin:
                    c.showPage()
                    draw_background()
                    draw_logo()
                    c.setFont(font, size)
                    c.setFillColorRGB(1, 1, 1)  # Testo bianco
                    y = self.page_height - self.margin
                c.drawString(x, y, line)
                y -= self.line_height + 4
            return y

        def draw_line(y_pos):
            c.setStrokeColorRGB(1, 1, 1)
            c.setLineWidth(1)
            c.line(self.margin, y_pos, self.page_width - self.margin, y_pos)

        def draw_two_column_info(x, y, info_left, info_right):
            max_width = 40
            spacing = 250
            for left, right in zip(info_left, info_right):
                y_left = write_wrapped_text(x, y, left, size=15, max_width=max_width)
                y_right = write_wrapped_text(x + spacing, y, right, size=15, max_width=max_width)
                y = min(y_left, y_right)
            return y

        def draw_image_with_aspect(image_path, x, y_top, max_width, max_height):
            try:
                img = ImageReader(image_path)
                iw, ih = img.getSize()
                aspect = ih / iw

                # Calcolare la larghezza e l'altezza dell'immagine in base alla larghezza massima
                width = max_width
                height = width * aspect

                # Se l'altezza supera l'altezza massima, ridimensiona in base all'altezza
                if height > max_height:
                    height = max_height
                    width = height / aspect

                # Calcolare la posizione X e Y per centrare l'immagine
                x_centered = (self.page_width - width) / 2  # Centra orizzontalmente
                y_centered = y_top - height  # Calcola la posizione Y

                # Disegna l'immagine centrata
                c.drawImage(img, x_centered, y_centered, width=width, height=height, preserveAspectRatio=True, mask='auto')
                return height
            except Exception as e:
                print(f"Errore immagine {image_path}: {e}")
                return 0

        def draw_footer():
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(1, 1, 1)  # Testo bianco per il footer
            c.drawString(self.margin, 20, "Contact us: Wizshotai@gmail.com")
            c.drawString(self.page_width - 150, 20, "2025 © WizShotAi")

        def draw_phase_block(title, image_path, frasi, y_start):
            # Imposta il font per il titolo
            c.setFont("Helvetica-Bold", 20)  # Titolo più grande
            c.setFillColorRGB(1, 1, 1)

            # Calcolare la larghezza del titolo per centrarlo
            title_width = c.stringWidth(title, "Helvetica-Bold", 20)
            x_centered = (self.page_width - title_width) / 2  # Calcola la posizione X per centrare il titolo

            # Disegna il titolo centrato
            c.drawString(x_centered, y_start, title.upper())  # Titolo centrato
            y = y_start - 25

            # Disegnare l'immagine centrata orizzontalmente
            image_height = draw_image_with_aspect(image_path, (self.page_width - 400) / 2, y, max_width=400, max_height=300)

            # Regolare la posizione y per tenere conto dell'immagine
            y = y - image_height - 10

            # Disegnare la linea di separazione sotto l'immagine
            draw_line(y)
            y -= 20

            # Scrivere il testo delle frasi
            x_text = self.margin  # Testo allineato a sinistra
            for frase in frasi:
                if y < self.margin:
                    c.showPage()
                    draw_background()
                    draw_logo()
                    # Ricalcolare la posizione x per centrare il titolo anche sulla nuova pagina
                    title_width = c.stringWidth(title, "Helvetica-Bold", 20)
                    x_centered = (self.page_width - title_width) / 2
                    c.setFont("Helvetica-Bold", 20)
                    c.setFillColorRGB(1, 1, 1)
                    c.drawString(x_centered, self.page_height - self.margin - 30, title.upper())
                    y = self.page_height - self.margin - 60
                y = write_wrapped_text(x_text, y, f"- {frase}", size=16, max_width=70)
            return y



        def draw_phase_page(title, image_path, frasi):
            c.showPage()
            draw_background()
            draw_logo()
            c.setFillColorRGB(1, 1, 1)
            y_start = self.page_height - self.margin - 60
            draw_phase_block(title, image_path, frasi, y_start)
            draw_footer()  # Footer fisso

        # Prima pagina con info e fase PREPARAZIONE
        draw_background()
        draw_logo()
        c.setFillColorRGB(1, 1, 1)

        y = self.page_height - self.margin - 90
        c.setFont("Helvetica-Bold", 20)
        y = write_wrapped_text(self.margin, y, "Informazioni giocatore:", font="Helvetica-Bold", size=20)

        info_left = [
            f"Name: {nome}",
            f"Date of Birth: {data_nascita}"
        ]
        info_right = [
            f"Surname: {cognome}",
            f"Posizione: {posizione}"
        ]
        y -= 10
        y = draw_two_column_info(self.margin, y, info_left, info_right)
        y -= 30

        # Fase PREPARAZIONE nella prima pagina
        preparazione_frasi = frasi_per_fase.get("preparazione", [])
        y = draw_phase_block("Preparazione", "static/temp_frames/PREPARAZIONE.jpg", preparazione_frasi, y)
        draw_footer()  # Footer fisso

        # Le altre fasi su pagine separate
        for fase in ["ESTENSIONE", "RILASCIO", "FOLLOW-THROUGH"]:
            frasi = frasi_per_fase.get(fase.lower(), [])
            image_path = f"static/temp_frames/{fase}.jpg"
            draw_phase_page(fase, image_path, frasi)

        c.save()
        print(f"✅ PDF creato: {self.output_file}")

    # Funzione per convertire lista piatta in dizionario per fase
    def raggruppa_frasi_per_fase(self, lista_frasi):
        frasi_per_fase = defaultdict(list)
        for frase in lista_frasi:
            frase_lower = frase.lower()
            if "follow-through" in frase_lower:
                fase = "follow-through"
            elif frase_lower.endswith("preparazione"):
                fase = "preparazione"
            elif frase_lower.endswith("estensione"):
                fase = "estensione"
            elif frase_lower.endswith("rilascio"):
                fase = "rilascio"
            else:
                continue
            frasi_per_fase[fase].append(frase)
        return frasi_per_fase






