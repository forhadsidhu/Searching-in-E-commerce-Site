from django.shortcuts import render

from django.views.generic import ListView, View
from .models import Product
from .forms import SearchForm
from elasticsearch_dsl import Search
from django.urls import reverse
from elasticsearch_dsl import A
from django.utils.http import urlencode
from elasticsearch_dsl.connections import connections


class HomeView(View):
    # model = Product
    # context_object_name = 'products'
    # template_name = 'home.html'

    def get(self, request):
        form = SearchForm(request.GET)
        ctx = {
            "form": form
        }

        if form.is_valid():
            # connections.create_connection()

            name_query = form.cleaned_data['name']

            if name_query:
                s = Search(index='daintree').query("match", name=name_query)
            else:
                # just show first ten documents
                s = Search(index='daintree')

            # adding minprice and maxprice in query
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')

            if min_price is not None or max_price is not None:
                price_query = dict()

                if min_price is not None:
                    price_query['gte'] = min_price
                if max_price is not None:
                    price_query['lte'] = max_price

                s = s.query('range', price=price_query)
            # Adding aggregations
            s.aggs.bucket("categories", "terms", field="category.keyword")

            if request.GET.get('category'):
                s = s.query('match', category=request.GET['category'])

            result = s.execute()
            ctx['products'] = result.hits

            category_aggregations = list()
            for bucket in result.aggregations.categories.buckets:
                category_name = bucket.key
                doc_count = bucket.doc_count

                category_url_params = request.GET.copy()
                category_url_params["category"] = category_name
                category_url = "{}?{}".format(reverse('home'), category_url_params.urlencode())
                category_aggregations.append({
                    "name": category_name,
                    "doc_count": doc_count,
                    "url": category_url
                })

            ctx["category_aggs"] = category_aggregations

            if "category" in request.GET:
                remove_category_search_params = request.GET.copy()
                del remove_category_search_params["category"]
                remove_category_url = "{}?{}".format(reverse("home"), remove_category_search_params.urlencode())
                ctx["remove_category_url"] = remove_category_url

        return render(request, 'home.html', ctx)
