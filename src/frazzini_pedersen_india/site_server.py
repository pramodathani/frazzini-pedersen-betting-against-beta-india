"""Serves the bundled companion page on this computer.

The page is a static site shipped inside the package, with the study's results as data files. Browsers refuse to load a page's data files straight from disk, which is why a small local web server is used rather than opening index.html directly.

Typical usage example, after pip install of this repository:

  bab-india-app
  bab-india-app --port 8123 --no-browser
"""

import argparse
import functools
import http.server
import pathlib
import socket
import webbrowser


class QuietRequestHandler(http.server.SimpleHTTPRequestHandler):
    """A static file handler that does not print a line for every request."""

    def log_message(self, format: str, *args: object) -> None:
        """Discards the per-request log line.

        Args:
            format: The text format of the message.
            *args: The values for the format.

        Returns:
            None.

        Raises:
            None.
        """
        del format, args


class SiteServerApplication:
    """The command-line program that serves the page locally.

    Attributes:
        site_directory: The folder holding index.html.
        default_port: The port tried first.
    """

    site_directory = pathlib.Path(__file__).resolve().parent / 'site'
    default_port = 8000

    @staticmethod
    def launch() -> None:
        """Runs the application; this is the target of the console command.

        Args:
            None.

        Returns:
            None.

        Raises:
            OSError: If no port could be opened.
        """
        SiteServerApplication().run()

    def run(self) -> None:
        """Starts the server and opens the browser until interrupted.

        Args:
            None.

        Returns:
            None.

        Raises:
            OSError: If no port could be opened.
            FileNotFoundError: If the site files are missing.
        """
        parser = argparse.ArgumentParser(
            description='Serve the Betting Against Beta page on this computer.'
        )
        parser.add_argument('--port', type=int, default=self.default_port)
        parser.add_argument('--no-browser', action='store_true')
        arguments = parser.parse_args()
        if not (self.site_directory / 'index.html').exists():
            raise FileNotFoundError(
                f'The page is missing from the package: {self.site_directory}'
            )
        port = self.free_port(arguments.port)
        handler = functools.partial(
            QuietRequestHandler, directory=str(self.site_directory)
        )
        server = http.server.ThreadingHTTPServer(('127.0.0.1', port), handler)
        address = f'http://127.0.0.1:{port}/'
        print(f'Serving the page at {address} (press Ctrl+C to stop)')
        if not arguments.no_browser:
            webbrowser.open(address)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('Stopped.')
        finally:
            server.server_close()

    def free_port(self, preferred: int) -> int:
        """Finds a free port, trying the preferred one and the next nineteen.

        Args:
            preferred: The port to try first.

        Returns:
            The first free port.

        Raises:
            OSError: If none of the twenty ports is free.
        """
        for port in range(preferred, preferred + 20):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                if probe.connect_ex(('127.0.0.1', port)) != 0:
                    return port
        raise OSError(f'No free port between {preferred} and {preferred + 19}')


if __name__ == '__main__':
    SiteServerApplication().run()
