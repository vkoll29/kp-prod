import web
from setup import get_message, handle_scenarios, welcome

urls = (
    '/(.*)', 'hooks'
)

app = web.application(urls, globals())


class hooks:
    def GET(self, name):
        if not name:
            name = 'unidentified person'
        return f'Hi {name}'

    def POST(self, req):
        # welcome()
        incoming_msg = get_message(web.data())
        handle_scenarios(web.data(), incoming_msg)

        # data = web.data()
        # print('Message Receivedclea')
        # print(data)
        #  kenya-power-331519

if __name__ == '__main__':
    app.run()
