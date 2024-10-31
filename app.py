from app import create_app

from dotenv import load_dotenv
load_dotenv()


app = create_app()




def handle_general_exception(e):
    """ Handle exceptions raised during a request. """
    app.logger.error(str(e), exc_info=True)
    response = {
        "error": str(e),
        "message": "An error occurred."
        }

@app.errorhandler(Exception)
def handle_error(e):
    return handle_general_exception(e)


if __name__ == '__main__':
    app.run(debug=True)
