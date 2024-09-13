from caveclient import CAVEclient
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", help="Token to save")
    args = parser.parse_args()

    client = CAVEclient()
    client.auth.save_token(token=args.token)