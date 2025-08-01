import io
import os

from helpers.permissions import IsSuperUser
from .models import Order, ExchangeRate, Receipt
from item.models import Item
from user.models import User
from .serializers import OrderSerializer, ExchangeRateSerializer
from rest_framework.permissions import IsAdminUser
from django.db.models.functions import Round
from helpers.views import BaseView
from customer.models import Address
from urllib.parse import urlparse, urlunparse
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse
from rest_framework import status
from django.core.files.base import ContentFile
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from django.db.models import F, Sum, ExpressionWrapper, FloatField
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime, timedelta, timezone as dt_timezone


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class OrderDetailView(BaseView):
    permission_classes = [IsAdminUser]
    
    Serializer = OrderSerializer
    Model = Order

    def delete(self, request, pk):
        if not request.user.is_active:
             return Response({"message": "Access Denied"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            order = Order.objects.get(id=pk, isActive=True, deliveredAt=None)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        order.isActive = False

        item = get_object_or_404(Item, pk=order.item.id)

        item.stockQuantity += order.quantity
        item.save()
        order.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
              
class ExchangeRateView(APIView):
    permission_classes = [IsAdminUser]
    def get_exchange_instance(self):
        # Always return the singleton instance, or create if not exists
        exchange, _ = ExchangeRate.objects.get_or_create()
        return exchange

    def get(self, request):
        exchange = self.get_exchange_instance()
        serializer = ExchangeRateSerializer(exchange)
        return Response(serializer.data)

    def put(self, request):
        exchange = self.get_exchange_instance()
        serializer = ExchangeRateSerializer(exchange, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MarkOrdersDeliveredAPIView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request, *args, **kwargs):
        date_str = request.data.get('date')
        address_id = request.data.get('address_id')

        if not date_str or not address_id:
            return Response({'error': 'Both "date" and "address_id" are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            local_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Create timezone-aware range
            local_start = timezone.make_aware(datetime.combine(local_date, datetime.min.time()))
            local_end = local_start + timedelta(days=1)

            utc_start = local_start.astimezone(dt_timezone.utc)
            utc_end = local_end.astimezone(dt_timezone.utc)

            updated_count = (
                Order.objects.filter(
                    orderedAt__gte=utc_start,
                    orderedAt__lt=utc_end,
                    address_id=address_id,
                    status='P'
                )
                .update(status='D', deliveredAt=timezone.now())
            )

            print(Order.objects.filter(address_id=address_id).count())

            return Response(
                {'message': f'{updated_count} order(s) marked as delivered.'},
                status=status.HTTP_200_OK
            )

        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateReceiptAPIView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request, address_id, driver_id, date_str):
        try:
            local_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        local_start = timezone.make_aware(datetime.combine(local_date, datetime.min.time()))
        local_end = local_start + timedelta(days=1)

        utc_start = local_start.astimezone(dt_timezone.utc)
        utc_end = local_end.astimezone(dt_timezone.utc)

        orders = Order.objects.filter(
            address_id=address_id,
            orderedAt__gte=utc_start,
            orderedAt__lt=utc_end,
            isActive=True
        )

        if not orders.exists():
            return Response({"error": "No orders found for the given address and date."}, status=status.HTTP_404_NOT_FOUND)

        receipt = Receipt.objects.create()
        pdf_file = self.create_thermal_pdf(request, orders, address_id, driver_id, local_date)
        filename = f"receipt_{address_id}_{local_date.strftime('%Y%m%d')}.pdf"
        receipt.file.save(filename, ContentFile(pdf_file), save=False)
        receipt.save()

        # Build the absolute URL
        absolute_url = request.build_absolute_uri(receipt.file.url)

        # Parse and remove query and fragment
        parsed = urlparse(absolute_url)
        clean_url = urlunparse(parsed._replace(query="", fragment=""))

        return Response({
            "message": "Receipt generated successfully.",
            "receipt_id": receipt.id,
            "file_url": clean_url
        }, status=status.HTTP_201_CREATED)

    def prepare_arabic(self, text):
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)
    
    def create_thermal_pdf(self, request, orders, address_id, driver_id, date):
        font_path = os.path.join(BASE_DIR, 'amiri', 'Amiri-Regular.ttf')
        pdfmetrics.registerFont(TTFont('Arabic', font_path))
        buffer = io.BytesIO()

        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return
        
        try:
            driver = User.objects.get(id=driver_id)
        except User.DoesNotExist:
            return

        # Estimate space needed: ~48 points per order (you can adjust)
        order_height = 48
        base_height = 100  # Header + footer space
        total_height = base_height + len(orders) * order_height
        thermal_width = 164  # 58mm in points

        # Create canvas with dynamic height
        c = canvas.Canvas(buffer, pagesize=(thermal_width, total_height))

        y_position = total_height - 20  # Start from top
        e = orders[0].liraRate

        c.setFont("Arabic", 8)
        c.drawString(10, y_position, f"On {date.strftime('%Y-%m-%d')}")
        y_position -= 10
        c.drawString(10, y_position, f"1.00 USD = {e} L.L")
        y_position -= 10

        c.setFont("Arabic", 8)
        c.drawString(10, y_position, self.prepare_arabic(f"For {address.customer.firstName} {address.customer.middleName} {address.customer.lastName}"))
        y_position -= 10

        c.setFont("Arabic", 8)
        c.drawString(10, y_position, self.prepare_arabic(f"Delivery: {driver.first_name} {driver.last_name}"))
        y_position -= 10

        c.setFont("Arabic", 8)
        c.drawString(10, y_position, self.prepare_arabic(f"Agent name: {request.user.first_name} {request.user.last_name}"))
        y_position -= 10

        c.drawString(10, y_position, "-" * 30)
        y_position -= 10

        total_amount = 0

        for order in orders:
            item_info = self.prepare_arabic(f"Item: {order.item.name[:20]} (Qty: {order.quantity})")
            c.drawString(10, y_position, item_info)
            y_position -= 12

            price_after_discount = order.item.price * order.quantity * (1 - order.discount / 100)
            c.drawString(10, y_position, self.prepare_arabic(f"Price: ${order.item.price} x {order.quantity} = ${price_after_discount:.2f}"))
            y_position -= 12

            total_amount += price_after_discount

            c.drawString(10, y_position, "-" * 30)
            y_position -= 12

        # Final total
        c.setFont("Arabic", 8)
        c.drawString(10, y_position, self.prepare_arabic(f"Total Amount: ${total_amount:.2f}"))
        y_position -= 10
        c.drawString(10, y_position, self.prepare_arabic(f"Total Amount: {(total_amount * e):,.2f} L.L"))

        c.save()

        buffer.seek(0)
        pdf_data = buffer.read()
        buffer.close()

        return pdf_data


class ItemSalesSummaryView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request, *args, **kwargs):
        # Get the year parameter
        year = request.query_params.get('year')
        tva = request.query_params.get('tva')
        if not year:
            return Response(
                {"error": "Year query parameter is required (e.g. ?year=2024)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate the year as a number
        try:
            year = int(year)
        except ValueError:
            return Response(
                {"error": "Year must be a valid number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Compute the summary
        orders = Order.objects.filter(orderedAt__year=year)
        if tva is not None:
            tva_flag = tva == "true"  # or bool conversion if needed
            orders = orders.filter(item__tva=tva_flag)

        summary = (
            orders
            .values(item_name=F('item__name'))
            .annotate(
                total_quantity=Sum('quantity'),
                total_sales=Round(
                    Sum(
                        ExpressionWrapper(
                            F('quantity') * F('item__price'),
                            output_field=FloatField()
                        )
                    ),
                    precision=2  # round to 2 decimal places
                )
            )
            .order_by('item_name')
        )

        return Response(summary, status=status.HTTP_200_OK)

class ExportItemSalesSummaryPDFView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Get the year and TVA status
        year = request.query_params.get('year')
        tva = request.query_params.get('tva')
        if not year:
            return Response({"error": "Year query parameter is required (e.g. ?year=2024)"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except ValueError:
            return Response({"error": "Year must be a valid number"}, status=status.HTTP_400_BAD_REQUEST)

        orders = Order.objects.filter(orderedAt__year=year)
        if tva is not None:
            tva_flag = tva == "true"
            orders = orders.filter(item__tva=tva_flag)

        summary = (
            orders
            .values(item_name=F('item__name'))
            .annotate(
                total_quantity=Sum('quantity'),
                total_sales=Round(
                    Sum(
                        ExpressionWrapper(
                            F('quantity') * F('item__price'),
                            output_field=FloatField()
                        )
                    ),
                    precision=2  # round to 2 decimal places
                )
            )
            .order_by('item_name')
        )

        if not summary:
            return Response({"error": "No data found for the given year and TVA status."}, status=status.HTTP_404_NOT_FOUND)

        # Create the PDF
        pdf_file = self.create_summary_pdf(year, summary)
        filename = f"item_sales_summary_{year}.pdf"

        # Return the PDF as a downloadable response
        response = FileResponse(io.BytesIO(pdf_file), as_attachment=True, filename=filename, content_type='application/pdf')
        return response

    def create_summary_pdf(self, year, summary):
        font_path = os.path.join(BASE_DIR, 'amiri', 'Amiri-Regular.ttf')
        pdfmetrics.registerFont(TTFont('Arabic', font_path))

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(595, 842))
        y_position = 800
        x_position = 40

        def prepare_arabic(text):
            """Helper to reshape and display Arabic text correctly."""
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped)

        # Header
        c.setFont("Arabic", 14)
        c.drawRightString(555, y_position, prepare_arabic(f"ملخص مبيعات الأصناف - {year}"))
        y_position -= 30

        # Table Header
        c.setFont("Arabic", 12)
        c.drawRightString(555, y_position, prepare_arabic("اسم المنتج"))
        c.drawRightString(300, y_position, prepare_arabic("الكمية الإجمالية"))
        c.drawRightString(180, y_position, prepare_arabic("إجمالي المبيعات"))
        y_position -= 20
        c.line(x_position, y_position, 555, y_position)
        y_position -= 20
        # Table Rows
        c.setFont("Arabic", 10)
        for item in summary:
            if y_position < 50:
                c.showPage()
                y_position = 800
                c.setFont("Arabic", 12)
                c.drawRightString(555, y_position, prepare_arabic("اسم المنتج"))
                c.drawRightString(300, y_position, prepare_arabic("الكمية الإجمالية"))
                c.drawRightString(180, y_position, prepare_arabic("إجمالي المبيعات"))
                y_position -= 20
                c.line(x_position, y_position, 555, y_position)
                y_position -= 20
                c.setFont("Arabic", 10)

            c.drawRightString(555, y_position, prepare_arabic(item['item_name']))
            c.drawRightString(300, y_position, str(item['total_quantity']))
            c.drawRightString(180, y_position, f"${item['total_sales']:.2f}")

            y_position -= 15

        c.save()
        buffer.seek(0)
        return buffer.read()
