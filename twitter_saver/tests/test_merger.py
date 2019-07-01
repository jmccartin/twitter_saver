import json

from twitter_saver.merger import main

db1 = [1, 2, 3, 4, 5]
db2 = [6, 7, 8]


def test_main(tmpdir):
    json1 = {"tweets": db1}
    json2 = {"tweets": db2}

    d = tmpdir.mkdir("sub1")

    f1 = d.join("db1.json")
    f1.write(json.dumps(json1))

    f2 = d.join("db2.json")
    f2.write(json.dumps(json2))

    o = d.join("db.json")

    main(file1=f1, file2=f2, output=o)

    assert json.loads(o.read())["tweets"] == db1 + db2, "The data in the merged file was wrong!"
