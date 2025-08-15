from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
import base64
import winreg

def add_to_system_path(new_path):
    # Open the SYSTEM PATH registry key
    key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        0, winreg.KEY_READ | winreg.KEY_WRITE
    )

    # Read the existing PATH
    value, _ = winreg.QueryValueEx(key, "Path")
    paths = value.split(";")

    if new_path not in paths:
        paths.append(new_path)
        new_value = ";".join(paths)
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_value)
        print(f"✅ Added to system PATH: {new_path}")
    else:
        print("⚠ Already in PATH")

    winreg.CloseKey(key)




def create_base64_image():
    image = Image.new('RGB', (100, 100), color=(255, 0, 0))
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode()}"

def get_jwt_token(user):
    """
    Helper method to get JWT token for a user.
    """
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def create_dummy_image():
        """Create a dummy image for testing."""
        # Create an image in memory
        image = Image.new('RGB', (100, 100), color = (255, 0, 0))
        image_file = io.BytesIO()
        image.save(image_file, format='JPEG')
        image_file.name = 'test_image.jpg'
        image_file.seek(0)
        return SimpleUploadedFile(image_file.name, image_file.read(), content_type='image/jpeg')

def login_required_resolver(resolver):
    def wrapper(self, info, *args, **kwargs):
        user = info.context.user
        if not user or not user.is_authenticated or not user.is_active:
            raise Exception("Authentication required")
        return resolver(self, info, *args, **kwargs)
    return wrapper

def calculate_total_profit(orders):
    total = 0
    for order in orders:
        total += (order.item.price * order.quantity) * (1 - order.discount / 100)
    return total