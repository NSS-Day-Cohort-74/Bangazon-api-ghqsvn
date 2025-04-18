"""
Author: Brian Henry
Purpose: To get all stores
Methods: GET
"""

"""View module for handling requests about stores"""
from bangazonapi.models import Customer, Product, Favorite
from bangazonapi.views.product import ProductSerializer
from bangazonapi.views.profile import CustomerSerializer
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status


class Store(ViewSet):
    def list(self, request):
        customers = Customer.objects.filter(store_name__isnull=False)

        stores = []

        for customer in customers:
            try:
                store_products = Product.objects.filter(customer=customer)

                serializered_store_products = ProductSerializer(
                    store_products,
                    many=True,
                )
                serialized_customer = CustomerSerializer(customer, many=False)
                store = {
                    "id": customer.id,
                    "seller": serialized_customer.data,
                    "name": customer.store_name,
                    "description": customer.store_description,
                    "products": serializered_store_products.data,
                }
                stores.append(store)
            except Exception as ex:
                return Response(
                    {
                        "details": "Problem getting store",
                        "error": ex,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(stores, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        customer = Customer.objects.get(pk=pk)

        try:
            store_products = Product.objects.filter(customer=customer)

            serializered_store_products = ProductSerializer(
                store_products, many=True, context={"request": request}
            )
            serialized_customer = CustomerSerializer(customer, many=False)

            store = {
                "id": customer.id,
                "seller": serialized_customer.data,
                "name": customer.store_name,
                "description": customer.store_description,
                "products": serializered_store_products.data,
                "is_liked": Favorite.objects.filter(
                    seller=customer, customer=request.user.customer
                ).exists(),
            }
        except Exception as ex:
            return Response(
                {
                    "details": "Problem getting store",
                    "error": ex.args[0],
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(store, status=status.HTTP_200_OK)
