import argparse
import logging
import sys
import os

import server

def main():
    parser = argparse.ArgumentParser(
        description="A local PyPI-compatible Cache Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("store_root",
                        help="Packages Store root, e.g. D:\pypistore")
    parser.add_argument("--address", default="0.0.0.0",
                        help="Address to bind to.")
    parser.add_argument("--port", default=8000, type=int,
                        help="Port to listen on.")
    parser.add_argument("--debug", default=False, action="store_true", 
                        help="Turn on debugging logging and output.")
    parser.add_argument("--reload", default=False, action="store_true", 
                        help="Turn on automatic reloading on code changes.")
    parser.add_argument("--processes", default=1, type=int, 
                        help="Number of processes to run")
    parser.add_argument("--upstream",
                        default="http://ni-pypi.amer.corp.natinst.com/simple/",
                        help="Main PyPI Server to use")
    args = parser.parse_args()

    # CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
    log_level = logging.DEBUG if args.debug else logging.INFO

    if not os.path.isdir(args.store_root):
        os.mkdir(args.store_root)

    log_filename = os.path.join(sys.path[0], "pypicachelog.txt")
    if os.path.exists(log_filename):
        os.remove(log_filename)
    
    logging.basicConfig(
        level=log_level,
        filename=log_filename,
        format="%(asctime)s [%(levelname)s] "
               "[%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info("Debugging: {0!r}".format(args.debug))
    logging.info("Reloading: {0!r}".format(args.reload))

    app = server.configure(
        upstream_server_url=args.upstream,
        disk_root=args.store_root,
        record_file_name="package_where.pkl")
    app.run(
        host=args.address,
        port=args.port,
        debug=args.debug,
        use_reloader=args.reload,
        processes=args.processes)

if __name__ == '__main__':
    main()
