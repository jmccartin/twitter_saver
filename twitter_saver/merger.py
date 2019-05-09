import argparse
import json
import os


def main(file1, file2, output):

    with open(os.path.expanduser(file1), "r") as f:
        jdb = json.load(f)
        db_1 = jdb.get("tweets")

    with open(os.path.expanduser(file2), "r") as f:
        jdb = json.load(f)
        db_2 = jdb.get("tweets")

    # Union the two tweet databases
    merged_tweets = db_1 + [tweet for tweet in db_2 if tweet not in db_1]

    jdb = {"tweets": list(merged_tweets)}

    with open(os.path.expanduser(output), "w") as f:
        json.dump(jdb, f)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--file1", "-f1", help="the first file to merge", type=str)
    parser.add_argument("--file2", "-f2", help="the second file to merge", type=str)
    parser.add_argument("--output", "-o", help="the name of the output file", type=str)

    args = parser.parse_args()

    main(args.file1, args.file2, args.output)
