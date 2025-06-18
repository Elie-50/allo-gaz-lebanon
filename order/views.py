import io
import os
from .models import Order, ExchangeRate, Receipt
from item.models import Item
from user.models import User
from .serializers import OrderSerializer, ExchangeRateSerializer
from rest_framework.permissions import IsAdminUser
from helpers.views import BaseView
from customer.models import Address
from django.utils.timezone import now
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
from rest_framework.permissions import AllowAny
from datetime import datetime
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import arabic_reshaper
from bidi.algorithm import get_display

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

    def get_exchange_instance(self):
        # Always return the singleton instance, or create if not exists
        exchange, created = ExchangeRate.objects.get_or_create()
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
    def post(self, request, *args, **kwargs):
        date_str = request.data.get('date')
        address_id = request.data.get('address_id')

        if not date_str or not address_id:
            return Response({'error': 'Both "date" and "address_id" are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            date = parse_date(date_str)
            if date is None:
                raise ValueError("Invalid date format. Use YYYY-MM-DD.")

            updated_count = (
                Order.objects
                .filter(orderedAt__date=date, address_id=address_id, status='P')
                .update(status='D', deliveredAt=now())
            )

            return Response(
                {'message': f'{updated_count} order(s) marked as delivered.'},
                status=status.HTTP_200_OK
            )

        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateReceiptAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, address_id, driver_id, date_str):
        """
        Generate and store a receipt PDF for a given address and date.
        This receipt will be designed for thermal printer compatibility.
        """
        # Convert date_str to a datetime object
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch orders for the given address and date
        orders = Order.objects.filter(address_id=address_id, orderedAt__date=date, isActive=True)

        if not orders.exists():
            return Response({"error": "No orders found for the given address and date."}, status=status.HTTP_404_NOT_FOUND)

        # Create the Receipt and generate the thermal-friendly PDF
        receipt = Receipt.objects.create()

        # Generate PDF for thermal printer
        pdf_file = self.create_thermal_pdf(request, orders, address_id, driver_id, date)

        # Save the PDF file to the model's file field
        receipt.file.save(f"receipt_{address_id}_{date.strftime('%Y%m%d')}.pdf", ContentFile(pdf_file), save=False)
        receipt.save()

        return Response({
            "message": "Receipt generated successfully.",
            "receipt_id": receipt.id,
            "file_url": request.build_absolute_uri(receipt.file.url)
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
        c.drawString(10, y_position, self.prepare_arabic(f"For {address.customer.firstName} {address.customer.lastName}"))
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
        c.drawString(10, y_position, self.prepare_arabic(f"Total Amount: {(total_amount * e):.2f}L.L"))

        c.save()

        buffer.seek(0)
        pdf_data = buffer.read()
        buffer.close()

        return pdf_data
