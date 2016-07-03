from werkzeug import routing, wrappers, exceptions


class Application:
    def __init__(self, tree):
        self.url_map = routing.Map([tree.get_url_rules()])
        self.endpoint_map = dict(tree.get_endpoints())
        self.tree = tree

    def __call__(self, environ, start_response):  # pragma: no cover
        response = self.dispatch_request(wrappers.Request(environ))
        return response(environ, start_response)

    def dispatch_request(self, request):
        adapter = self.get_url_adapter(request)
        try:
            endpoint, values = adapter.match()
            return self.serve_endpoint(request, endpoint, values)
        except exceptions.NotFound as e:
            return e
        except exceptions.HTTPException as e:  # pragma: no cover
            return e

    def get_url_adapter(self, request):
        return self.url_map.bind_to_environ(request.environ)

    def get_url_for(self, request):
        return self.get_url_adapter(request).build

    def serve_endpoint(self, request, endpoint, values):
        try:
            handler_class = self.endpoint_map[endpoint]
        except KeyError:
            raise exceptions.NotFound('Endpoint not found.')
        handler = handler_class(self, request)
        return handler.entrypoint(**values)
