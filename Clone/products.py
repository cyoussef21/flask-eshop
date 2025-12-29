from http.client import responses
from urllib.parse import parse_qsl

import requests

# response = requests.get('https://dummyjson.com/products')
# print(response.json())

# response = requests.get('https://dummyjson.com/products/category-list')
# print(response.json())
# #
cat = ['beauty', 'fragrances', 'furniture', 'groceries', 'home-decoration', 'kitchen-accessories',
       'laptops', 'mens-shirts', 'mens-shoes', 'mens-watches', 'mobile-accessories', 'motorcycle',
       'skin-care', 'smartphones', 'sports-accessories', 'sunglasses', 'tablets', 'tops', 'vehicle',
       'womens-bags', 'womens-dresses', 'womens-jewellery', 'womens-shoes', 'womens-watches']

response = requests.get('https://dummyjson.com/products/category/laptops')
data = response.json()['products']
product = data[0]
print(product)

for product in data:
    name = product['title']
    description = product['description']
    price = product['price']
    discount = product['discountPercentage']/100
    thumbnail = product['thumbnail']
    image = product['images'][0]
    category = 'electronics'

    new_product = f'''
        product_name={name},
        product_description={description},
        product_price={price},
        product_discount={discount},
        product_thumbnail={thumbnail},
        product_image={image},
        product_category={category}
    '''
    print(new_product)