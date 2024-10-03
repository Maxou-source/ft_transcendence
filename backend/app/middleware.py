class AddTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add a custom attribute to the request
        request.token = 'sfgljdsfhflhfdg'
        # Call the next middleware or view
        response = self.get_response(request)
        return response