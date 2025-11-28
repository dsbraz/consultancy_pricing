# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from sqlalchemy.orm import Session

from app.models.models import Project
from app.services.pricing_service import PricingService
from app.services.calendar_service import CalendarService


class PNGExportService:
    def __init__(self, db: Session):
        self.db = db
        self.pricing_service = PricingService(db)
        self.calendar_service = CalendarService(country_code="BR")

        self.width = 1600
        self.height = 3000  # large enough to accommodate any content
        self.padding = 40
        self.line_height = 30

        self.bg_color = (255, 255, 255)
        self.primary_color = (68, 114, 196)
        self.text_color = (33, 33, 33)
        self.secondary_text = (107, 114, 128)
        self.border_color = (229, 231, 235)
        self.highlight_bg = (249, 250, 251)

    def export_project_to_png(self, project: Project) -> BytesIO:
        """
        Export a complete project to a PNG image suitable for commercial proposals.
        """
        img = Image.new("RGB", (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img, "RGBA")

        try:
            font_title = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40
            )
            font_heading = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20
            )
            font_normal = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14
            )
            font_small = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12
            )
        except (OSError, IOError):
            font_title = ImageFont.load_default()
            font_heading = ImageFont.load_default()
            font_normal = ImageFont.load_default()
            font_small = ImageFont.load_default()

        y_position = self.padding

        y_position = self._draw_title(draw, project.name, y_position, font_title)
        y_position += 15

        y_position = self._draw_project_info(draw, project, y_position, font_small)
        y_position += 25

        y_position = self._draw_section_header(
            draw, "Tabela de Alocação", y_position, font_heading
        )
        y_position = self._draw_allocation_table(draw, project, y_position, font_small)
        y_position += 25

        y_position = self._draw_section_header(
            draw, "Resumo Financeiro", y_position, font_heading
        )
        y_position = self._draw_financial_summary(
            draw, project, y_position, font_normal
        )

        # Crop image to actual content height
        final_height = y_position + self.padding
        img = img.crop((0, 0, self.width, final_height))

        output = BytesIO()
        img.save(output, format="PNG", quality=95)
        output.seek(0)
        return output

    def _draw_title(self, draw, title, y_pos, font):
        """Draw project title"""
        draw.rectangle(
            [(0, y_pos - 10), (self.width, y_pos + 50)], fill=self.primary_color
        )

        if isinstance(title, bytes):
            title = title.decode("utf-8")

        draw.text((self.padding, y_pos), title, fill=(255, 255, 255), font=font)

        return y_pos + 60

    def _draw_section_header(self, draw, title, y_pos, font):
        """Draw section header"""
        draw.text((self.padding, y_pos), title, fill=self.primary_color, font=font)

        draw.line(
            [(self.padding, y_pos + 25), (self.width - self.padding, y_pos + 25)],
            fill=self.primary_color,
            width=2,
        )

        return y_pos + 35

    def _draw_project_info(self, draw, project, y_pos, font):
        """Draw basic project information"""
        info_items = [
            f"Data de Início: {project.start_date.strftime('%d/%m/%Y')}",
            f"Duração: {project.duration_months} meses",
        ]

        for item in info_items:
            draw.text((self.padding, y_pos), item, fill=self.secondary_text, font=font)
            y_pos += 18

        return y_pos

    def _draw_allocation_table(self, draw, project, y_pos, font):
        """Draw allocation table with weekly breakdown (only non-empty weeks)"""
        if not project.allocations:
            draw.text(
                (self.padding, y_pos),
                "Nenhuma alocação definida",
                fill=self.secondary_text,
                font=font,
            )
            return y_pos + 30

        all_weeks = self.calendar_service.get_weekly_breakdown(
            project.start_date, project.duration_months
        )

        weeks_with_hours = set()
        for allocation in project.allocations:
            for wa in allocation.weekly_allocations:
                if wa.hours_allocated > 0:
                    weeks_with_hours.add(wa.week_number)

        weeks = [w for w in all_weeks if w["week_number"] in weeks_with_hours]

        if not weeks:
            draw.text(
                (self.padding, y_pos),
                "Nenhuma hora alocada",
                fill=self.secondary_text,
                font=font,
            )
            return y_pos + 30

        start_x = self.padding
        end_x = self.width - self.padding
        table_width = end_x - start_x

        name_col_width = 200
        role_col_width = 160
        rate_col_width = 100
        total_col_width = 80

        remaining_width = (
            table_width
            - name_col_width
            - role_col_width
            - rate_col_width
            - total_col_width
        )
        cell_width = remaining_width // max(len(weeks), 1)

        header_y = y_pos

        draw.rectangle(
            [(start_x, header_y), (end_x, header_y + 40)],
            fill=self.highlight_bg,
            outline=self.border_color,
        )

        x_pos = start_x + 5
        draw.text(
            (x_pos, header_y + 12), "Profissional", fill=self.text_color, font=font
        )
        x_pos += name_col_width

        draw.text(
            (x_pos, header_y + 12), "Função/Nível", fill=self.text_color, font=font
        )
        x_pos += role_col_width

        draw.text(
            (x_pos, header_y + 12), "Taxa (R$/h)", fill=self.text_color, font=font
        )
        x_pos += rate_col_width

        for week in weeks:
            week_label = f"S{week['week_number']}"
            draw.text(
                (x_pos + 5, header_y + 12), week_label, fill=self.text_color, font=font
            )
            x_pos += cell_width

        draw.text((x_pos + 5, header_y + 12), "Total", fill=self.text_color, font=font)

        y_pos = header_y + 40

        # Rows
        for allocation in project.allocations:
            professional = allocation.professional

            # Row background
            if project.allocations.index(allocation) % 2 == 0:
                draw.rectangle(
                    [(start_x, y_pos), (end_x, y_pos + 30)],
                    fill=(252, 252, 252),
                    outline=self.border_color,
                )
            else:
                draw.rectangle(
                    [(start_x, y_pos), (end_x, y_pos + 30)], outline=self.border_color
                )

            x_pos = start_x + 5
            draw.text(
                (x_pos, y_pos + 8),
                professional.name[:24],
                fill=self.text_color,
                font=font,
            )
            x_pos += name_col_width

            role_level = f"{professional.role} {professional.level}"[:20]
            draw.text((x_pos, y_pos + 8), role_level, fill=self.text_color, font=font)
            x_pos += role_col_width

            draw.text(
                (x_pos, y_pos + 8),
                f"{allocation.selling_hourly_rate:.0f}",
                fill=self.text_color,
                font=font,
            )
            x_pos += rate_col_width

            weekly_hours_map = {
                wa.week_number: wa.hours_allocated
                for wa in allocation.weekly_allocations
            }
            total_hours = 0

            for week in weeks:
                hours = weekly_hours_map.get(week["week_number"], 0)
                total_hours += hours
                if hours > 0:
                    draw.text(
                        (x_pos + 5, y_pos + 8),
                        f"{hours:.0f}",
                        fill=self.text_color,
                        font=font,
                    )
                x_pos += cell_width

            draw.text(
                (x_pos + 5, y_pos + 8),
                f"{total_hours:.0f}h",
                fill=self.text_color,
                font=font,
            )

            y_pos += 30

        # Total row at bottom of table
        y_pos += 5
        draw.rectangle([(start_x, y_pos), (end_x, y_pos + 35)], fill=self.primary_color)

        # Calculate grand total hours
        grand_total_hours = sum(
            sum(wa.hours_allocated for wa in allocation.weekly_allocations)
            for allocation in project.allocations
        )

        draw.text(
            (start_x + 10, y_pos + 10),
            "TOTAL DE HORAS DO PROJETO:",
            fill=(255, 255, 255),
            font=font,
        )

        total_text = f"{grand_total_hours:.1f}h"
        draw.text(
            (end_x - 100, y_pos + 10), total_text, fill=(255, 255, 255), font=font
        )

        return y_pos + 45

    def _draw_financial_summary(self, draw, project, y_pos, font):
        pricing = self.pricing_service.calculate_project_pricing(project)

        box_padding = 20
        box_y = y_pos
        box_height = 95

        draw.rectangle(
            [(self.padding, box_y), (self.width - self.padding, box_y + box_height)],
            fill=self.highlight_bg,
            outline=self.primary_color,
            width=2,
        )

        y_pos = box_y + box_padding
        x_label = self.padding + box_padding
        x_value = self.width - self.padding - 200
        items = [
            ("Impostos:", f"R$ {pricing['total_tax']:,.2f}"),
        ]

        for label, value in items:
            draw.text((x_label, y_pos), label, fill=self.secondary_text, font=font)
            draw.text((x_value, y_pos), value, fill=self.text_color, font=font)
            y_pos += 25
        y_pos += 5
        draw.rectangle(
            [
                (self.padding + 10, y_pos - 5),
                (self.width - self.padding - 10, y_pos + 30),
            ],
            fill=self.primary_color,
        )

        draw.text((x_label, y_pos + 5), "PREÇO FINAL:", fill=(255, 255, 255), font=font)
        draw.text(
            (x_value, y_pos + 5),
            f"R$ {pricing['final_price']:,.2f}",
            fill=(255, 255, 255),
            font=font,
        )

        return y_pos + 45
