
from argument_usage_context import *

SPECIAL_ARGS = "/Users/salspaugh/queryexplorer/data.storm/args/args_template_cnts_user_cnts_to_explore.csv"

def read_special_args():
    args = {}
    with open(SPECIAL_ARGS) as special_args:
        for line in special_args.readlines():
            line = line.strip()
            if line == "":
                continue
            if line.find("#") > -1:
                continue
            parts = line.split(',')
            raw = parts[2]
            converted = raw.strip('"').lower()
            if converted in ["get", "head", "post"]:
                converted = "get|head|post"
            if converted[0:5] == "date_":
                converted = "date_*"
            if converted[0:4] == "fail":
                converted = "fail"
            if converted in ["true", "false"]:
                converted = "true|false"
            if converted.find("/var/log") == 0:
                converted = "/var/log/*"
            if converted.find("login") > -1:
                converted = "login"
            if converted.find("access") > -1:
                converted = "access_*"
            if not converted in args:
                args[converted] = []
            args[converted].append(raw)
    #print "Number of args:", len(args)
    labels = []
    for (label, placement) in labeling():
        rawlist = args[label]
        labels.append(((label, placement), rawlist))
    return labels

def labeling():
    return [
          ("type",        1),
          #("t",           2),
          #("key",         3),
          #("value",       4),
          ("true|false",  5),
          #("*",           6),
          #("index",       7),
          #("source",      8),
          #("event",       9),
          #("_raw",        10),

          ("0",           11),         
          #("1",           12),
          #("10",          13),
          #("100",         14),
          #("1000",        15),
          #("10000",       16),
          ("60",          17),
          ("1024",        18),

          #("2",           21),
          #("3",           22),
          #("4",           23),
          #("5",           24),
          #("6",           25),
          #("7",           26),
          #("15",          27),
          #("20",          28),
          #("50",          29),

          #("200",         31),
          #("301",         32),
          #("302",         33),
          #("304",         34),
          #("400",         35),
          #("401",         36),
          #("403",         37),
          #("404",         38),
          #("499",         39),
          #("500",         40),

          #("info",        41),
          #("debug",       42),
          #("warn",        43),
          #("warning",     44),
          #("exception",   45),
          #("critical",    46),
          #("severe",      47),
          ("error",       48),
          #("fail",        49),
          #("other",       50),
          
          #("node",        51),
          #("router",      52),
          #("app",         53),
          #("backup",      54),
          #("dev",         55),
          #("out",         56),
          #("prod",        57),
          #("web",         58),
          #("email",       59),
          #("worker",      60),
          
          #("/var/log/*",  61),
          #("sshd",        62),
          #("syslog",      63),
          #("root",        64),
          ("queue",       65),
          ("env",         66),
          #("title",       67),
          ("metric",      68),
          ("module",      69),
          ("application", 70),

          #("access_*",        71),
          #("get|head|post",   72),
          ("login",	        73),
          ("connection",	    74),
          #("session",	        75),
          ("useragent",	    76),
          ("method",	        77),
          ("referer_domain",  78),
          #("url",	            79),
          #("cookie",	        80),

          #("denied",      81),
          #("refused",     82),
          #("purchase",	83),
          ("account",	    84),
          ("referer",	    85),
          #("click",       86),
          ("activity",    87),
          ("uri",	        88),
          #("uri_domain",	89),
          #("uri_path",	90),
          
          ("client",	    91),
          #("client_ip",	92),
          ("clientip",	93),
          #("ip",	        94),
          ("user",	    95),
          ("user_id",	    96),
          ("userid",	    97),
          ("uid",	        98),
          ("screen_name",	99),
          ("name",	    100),
          
          ("status",      101),
          ("level",       102),
          ("severity",    103),
          #("total",       104),
          #("amount",      105),
          #("size",        106),
          #("measurement", 107),
          #("linecount",   108),
          ("count",       109),
          ("bytes",       110),
          
          #("password",    111),
          #("memory",      112),
          #("group",       113),
          ("process",     114),
          ("pid",         115),
          ("priority",    116),
          ("code",        117),
          ("desc",        118),
          #("msg",         119),
          ("message",     120),
          
          #("channel",     121),
          #("controller",  122),
          #("cmd",         123),
          #("command",     124),
          ("action",      125),
          ("reason",      126),
          #("host",        127),
          ("path",        128),
          #("device",      129),
          #("device_type", 130),
          
          #("_time",	    131),
          ("timeout",	    132),
          #("timestamp",	133),
          #("timestartpos",134),
          #("timeendpos",	135),
          ("req_time",	136),
          ("time",	    137),
          ("time_taken",	138),
          ("duration",    139),

          ("id",              141),
          ("server",          142),
          ("eventtype",       143),
          #("splunk_server",   144),
          #("punct",           144),
          #("act",             145),
          ("src",             146),
          ("date",            147),
          #("date_*",          148),
          #("href",            149),
          #("proto",           150),
    ]


def main():
    args = {}
    for ((label, placement), arglist) in read_special_args():
        context = extract_context(label, arglist)
        if not label in args:
            args[label] = {}
        for (usage, count) in context.get_usages_and_counts():
            if count == 0: continue
            if not usage in args[label]:
                args[label][usage] = 0
            args[label][usage] += count
    for (arg, cmd_counts) in args.iteritems():
        print json.dumps([arg, cmd_counts.items()])

main()
