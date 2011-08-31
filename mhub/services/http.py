import os
import yaml

from twisted.web import resource, static
from jinja2 import Environment, FileSystemLoader


class HTTPService(resource.Resource):
 
    cs = None
    isLeaf = True


    def getChild(self, name, request):
        
        if name == "":
            return self
        return resource.Resource.getChild(self, name, request)


    def get_menu(self, filename):

        stream = file(filename, "r")
        menu = yaml.load(stream)
        return menu


    def render_GET(self, request):

        if request.path.startswith("/app/send"):
            return self.render_app_send(request)
        else:
            return self.render_index(request)


    def render_index(self, request):

        cfg_web = self.cs.cfg.get("web")
        web_dir = cfg_web.get("web_dir")
        template_dir = os.path.join(web_dir, "templates")
        template_filename = cfg_web.get("template", "default.html")
        menu_filename = os.path.join(web_dir, "menu.yml")
        menu = self.get_menu(menu_filename)

        env = Environment(loader=FileSystemLoader(template_dir))
        tmpl = env.get_template(template_filename)
        ctx = dict(menu=menu)
        rendered = tmpl.render(ctx)

        return str(rendered)


    def render_app_send(self, request):

        args = request.args
 
        action = args.get("action", "")

        success = False

        if len(action) > 0:

            del args["action"]
            action_str = action[0]

            for k, v in args.iteritems():
                val = v[0]
                if val.lower() == "true":
                    val = True
                elif val.lower() == "false": 
                    val = False
                args[k] = val

            msg = dict(action=action, params=args)
    
            self.cs.amqp_send_message(msg)
            success = True
        
        return "OK" if success else "ERROR"
