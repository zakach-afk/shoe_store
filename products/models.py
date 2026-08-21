from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    order = models.IntegerField(default=0, help_text="Order position in navigation")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_featured = models.BooleanField(default=False, help_text="Display on homepage featured drops section")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def discount_percentage(self):
        if self.sale_price and self.regular_price > self.sale_price:
            discount = ((self.regular_price - self.sale_price) / self.regular_price) * 100
            return int(discount)
        return 0

    @property
    def active_price(self):
        """Returns the sale price if available, otherwise regular price"""
        return self.sale_price if self.sale_price else self.regular_price

    @property
    def main_image(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        non_sole = self.images.exclude(image__icontains='medicated_inner_sole').exclude(image__icontains='sole').first()
        if non_sole:
            return non_sole
        return self.images.first()

    @property
    def secondary_image(self):
        main = self.main_image
        if main:
            second = self.images.exclude(id=main.id).first()
            if second:
                return second
        return None

    @property
    def is_medicated(self):
        return 'medicated' in self.name.lower() or 'medicated' in self.description.lower()


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=10, help_text="e.g. 39, 40, 41, 42, 43")
    stock = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.product.name} - Size {self.size}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_primary', 'id']

    def __str__(self):
        return f"Image for {self.product.name}"


# --- ORDERS & CHECKOUT MODELS ---

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    shipping_address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    size = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        product_name = self.product.name if self.product else "Deleted Product"
        return f"{self.quantity}x {product_name} (Size {self.size})"