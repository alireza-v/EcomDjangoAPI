from rest_framework import serializers

from product.models import Category, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["name", "price", "image"]


class SubCategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["title", "products", "subcategories"]

    def get_subcategories(self, obj):
        children = obj.subcategories.all()
        serializer = SubCategorySerializer(children, many=True)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["title", "products", "subcategories"]
