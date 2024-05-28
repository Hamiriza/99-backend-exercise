import tornado.ioloop
import tornado.web
import tornado.log
import tornado.options
import json
import logging
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

class PublicAPIService(tornado.web.Application):
    def __init__(self, handlers, **kwargs):
        settings = dict(
            user_service_url="http://localhost:6000",
            listing_service_url="http://localhost:6001",
        )
        super().__init__(handlers,**kwargs, **settings)

class BaseHandler(tornado.web.RequestHandler):
    @property
    def user_service_url(self):
        return self.application.settings["user_service_url"]

    @property
    def listing_service_url(self):
        return self.application.settings["listing_service_url"]

class PublicUsersHandler(BaseHandler):
    async def post(self):
        client = AsyncHTTPClient()
        data = json.loads(self.request.body)
        request = HTTPRequest(
            url=f"{self.user_service_url}/users",
            method="POST",
            body=f"name={data['name']}",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        try:
            response = await client.fetch(request)
            self.set_status(response.code)
            self.write(response.body)
            logging.info("User created through Public API: %s", data['name'])
        except Exception as e:
            self.set_status(500)
            self.write(json.dumps({"result": False, "error": str(e)}))
            logging.error("Failed to create user through Public API: %s", e)

class PublicListingsHandler(BaseHandler):
    async def get(self):
        client = AsyncHTTPClient()
        params = self.request.query
        try:
            response = await client.fetch(f"{self.listing_service_url}/listings?{params}")
            listings = json.loads(response.body).get('listings', [])
            logging.info("Fetched listings through Public API: %s", listings)

            # Enrich listings with user data
            for listing in listings:
                user_response = await client.fetch(f"{self.user_service_url}/users/{listing['user_id']}")
                listing['user'] = json.loads(user_response.body).get('user', {})

            self.write(json.dumps({"result": True, "listings": listings}))
        except Exception as e:
            self.set_status(500)
            self.write(json.dumps({"result": False, "error": str(e)}))
            logging.error("Failed to fetch listings through Public API: %s", e)

    async def post(self):
        client = AsyncHTTPClient()
        data = json.loads(self.request.body)
        request = HTTPRequest(
            url=f"{self.listing_service_url}/listings",
            method="POST",
            body=f"user_id={data['user_id']}&listing_type={data['listing_type']}&price={data['price']}",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        try:
            response = await client.fetch(request)
            self.set_status(response.code)
            self.write(response.body)
            logging.info("Listing created through Public API: %s", data)
        except Exception as e:
            self.set_status(500)
            self.write(json.dumps({"result": False, "error": str(e)}))
            logging.error("Failed to create listing through Public API: %s", e)

def make_app(options):
    return PublicAPIService([
            (r"/public-api/users", PublicUsersHandler),
            (r"/public-api/listings", PublicListingsHandler),
        ], debug=options.debug)           

if __name__ == "__main__":
    tornado.options.define("port", default=6002)
    tornado.options.define("debug", default=True)
    tornado.options.parse_command_line()
    options = tornado.options.options

    app = make_app(options)
    app.listen(options.port)
    logging.info("Starting public api service. PORT: {}, DEBUG: {}".format(options.port, options.debug))

    tornado.ioloop.IOLoop.current().start()