

import json
import sys

from itertools import chain
from queryexplorer import connect_db

SPECIAL_ARGS = "/Users/salspaugh/queryexplorer/data.storm/args/args_template_cnts_user_cnts_to_explore.csv"
ROWS = 15
COLS = 10
FONT_SIZE = 20.0

class Context(object):      # of argument foo

    def __init__(self, arg):
        
        self.arg = arg
        
        self.grp_filtered_on_as_value = 0  # SEARCH =foo
        self.grp_filtered_on_as_field = 0  # SEARCH foo=
        self.grp_argument_to_top = 0             # TOP foo
        self.grp_projected = 0          # FIELDS(PLUS) foo TABLE foo
        self.grp_unprojected = 0        # FIELDS(MINUS) foo
        self.grp_grouped_by = 0         # by foo
        self.grp_argument_renamed_as = 0         # as foo
        self.grp_argument_to_aggregation = 0         # STATS(COUNT) foo
        self.grp_argument_to_arithmetic_transformation = 0         # EVAL, STATS
        self.grp_field_used_in_conditional = 0
        self.grp_argument_to_option = 0
        self.grp_sorted_by = 0
        self.grp_value_used_in_other_transformation = 0
        self.grp_field_used_in_other_transformation = 0
        self.grp_field_used_as_function_domain = 0

        self.contexts = sorted(filter(lambda x: x[0:4] == "grp_", self.__dict__.keys()))
        self.colors = [
                        "#843c39", # dark red
                        "#b5cf6b", # light green
                        "#5254a3", # dark purple-blue
                        "#de9ed6", # light pink
                        "#637939", # dark green 
                        "#9c9ede", # light purple
                        "#8c6d31", # dark yellow
                        "#d6616b", # light red
                        "#7b4173", # dark purple-red
                        "#e7ba52", # light yellow
                        "#a55194", # dark pink
                        "#8ca252", # green
                        "#6b6ecf", # purple
                        "#bd9e39", # yellow
                        "#ce6dbd", # pink
                        "#cedb9c", # lighter green
                        #"#e7cb94", # lighter yellow
                        #"#e7969c", # lighter red
                        #"#ad494a", # red
                    ]
        self.grayscale = [
            #(pattern, color)
            #("O", "#FFFFFF"),
            ("x", "#FFFFFF"),
            ("o", "#666666"),
            ("o", "#CCCCCC"),
            ("o", "#FFFFFF"),
            (".", "#666666"),
            (".", "#CCCCCC"),
            (".", "#FFFFFF"),
            ("", "#000000"),
            ("", "#666666"),
            ("", "#999999"),
            ("", "#CCCCCC"),
            ("+", "#666666"),
            ("+", "#CCCCCC"),
            ("+", "#FFFFFF"),
            ("\\", "#666666"),
            ("\\", "#CCCCCC"),
            ("\\", "#FFFFFF"),
            #("*", "#FFFFFF"),
        ]
    
    def __lt__(self, other):
        return ([getattr(self, attr) for attr in self.contexts] < [getattr(other, attr) for attr in other.contexts])

    def __eq__(self, other):
        return ([getattr(self, attr) for attr in self.contexts] == [getattr(other, attr) for attr in other.contexts])

    def nothing_set(self):
        for attr in self.contexts:
            if getattr(self, attr):
                return False
        return True
    
    def number_set(self):
        return sum([getattr(self, attr) for attr in self.contexts])

    def get_counts(self):
        return [getattr(self, attr) for attr in self.contexts]

    def get_usages_and_counts(self):
        return [(attr.replace("grp_", "").replace("_"," "), getattr(self, attr)) for attr in self.contexts]

    def get_labels(self):
        return [s.replace("grp_", "").replace("_", " ") for s in self.contexts]

    def get_colors(self):
        return self.colors

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

def extract_context(cleanarg, rawlist):
    c = Context(cleanarg)
    db = connect_db()
    number_commands = 0
    #print
    for arg in rawlist:
        #print "arg: ", arg
        cursor = db.execute("SELECT command, text FROM queries, commands, args \
                                WHERE queries.id = args.query_id \
                                AND args.command_id = commands.id \
                                AND arg=?", [arg])
        for (command, query) in cursor.fetchall():
            #print "\tcmd:", command

            number_commands += 1
            set = False
            set_field = False
            if command.find("SEARCH") == 0 or command.find("WHERE") == 0:
                for comparator in ["=", ">", "<", "!=", "=="]:
                    if query.find(arg + comparator) > -1 or query.find(arg + " " + comparator) > -1:
                        c.grp_filtered_on_as_field += 1
                        set = True
                        set_field = True
                if not set_field:        
                    c.grp_filtered_on_as_value += 1
                    set = True

            if command.find("DEDUP") == 0:
                c.grp_filtered_on_as_field += 1
                set = True

            if command.find("TOP") == 0:
                try:
                    int(c.arg)
                    c.grp_argument_to_option += 1
                    set = True
                except:
                    c.grp_argument_to_top += 1
                    set = True

            if command.find("SORT") == 0:
                try:
                    int(arg)
                    c.grp_argument_to_option += 1
                    set = True
                except:
                    if query.find("=" + arg) == -1:
                        c.grp_sorted_by += 1
                        set = True

            if command.find("FIELDS(PLUS)") == 0 or command.find("TABLE") == 0 or command.find("EXPORT") == 0:
                c.grp_projected += 1
                set = True

            if command.find("FIELDS(MINUS)") == 0:
                c.grp_unprojected += 1
                set = True

            if command.find("INPUTLOOKUP") == 0 or command.find("ABSTRACT") == 0:
                if query.find("=" + arg) > -1:
                    c.grp_argument_to_option += 1
                    set = True

            if command.find("HEAD") == 0:
                c.grp_argument_to_option += 1
                set = True

            if command.find("STATS") == 0 or command.find("TIMECHART") == 0 or command.find("CHART") == 0:
                for function in ["count", "min", "avg", "max", "sum", "c", "values", "range", "last", "distinct_count", "dc", "mode", "var"]:
                    if query.find(function + " " + arg) > -1 or query.find(function + "(" + arg + ")") > -1 or query.find(function + " (" + arg + ")") > -1:
                        c.grp_argument_to_aggregation += 1
                        set = True
            
            if (command.find("STATS") == 0 or command.find("EVAL") == 0 or command.find("CHART") == 0 or command.find("TIMECHART") == 0 or command.find("RENAME") == 0) and command.find("AS") > -1:
                if query.find("as " + arg) > -1 or query.find("AS " + arg) > -1:
                    c.grp_argument_renamed_as += 1
                    set = True
            
            if (command.find("STATS") == 0 or command.find("EVAL") == 0 or command.find("CHART") == 0 or command.find("TIMECHART") == 0) and command.find("OVER") > -1:
                if query.find("over " + arg) > -1 or query.find("OVER " + arg) > -1:
                    c.grp_field_used_as_function_domain += 1
                    set = True

            if (command.find("STATS") == 0 or command.find("EVAL") == 0 or command.find("CHART") == 0 or command.find("TIMECHART") == 0) and command.find("BY") > -1:
                if query.find("by " + arg) > -1 or query.find("BY " + arg) > -1 or query.find("by") < query.rfind(arg):
                    c.grp_grouped_by += 1
                    set = True

            if command.find("EVAL") > -1 and (command.find("DIVIDES") > -1 or command.find("TIMES") > -1 or command.find("PLUS") > -1):
                c.grp_argument_to_arithmetic_transformation += 1
                set = True

            if command.find("EVAL") > -1:
                if query.find(arg + "=") > -1:
                    c.grp_field_used_in_conditional += 1
                    set = True
                else:
                    c.grp_value_used_in_other_transformation += 1
                    #print command
                    set = True

            if command.find("MULTIKV") == 0 or command.find("CONVERT") == 0 or command.find("BUCKET") == 0 or command.find("REX") == 0 or command.find("REPLACE") == 0 or command.find("REGEX") == 0 or command.find("MAKEMV") == 0 or command.find("MVEXPAND") == 0:
                c.grp_field_used_in_other_transformation += 1
                #print command
                set = True
            
            if command.find("TIMECHART") == 0:
                if query.find("=" + arg) > -1 or query.find("= " + arg) > -1:
                    try:
                        int(arg)
                        set = True
                        c.grp_argument_to_option += 1
                    except:
                        pass

            if arg == "false" and not set:
                c.grp_argument_to_option += 1
                set = True

            if not set:
                print "\t\t\tNo case for this one!"
    
    db.close()
    if c.number_set() < number_commands: 
        print "Missed a case!", arg
        exit()
    return c

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                ha='center', va='bottom', size='x-large')

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
    cmds = list(set(chain.from_iterable([v.keys() for v in args.values()])))
    cmds_idxs = zip(cmds, range(len(cmds)))
    #for (cmd, idx) in cmds_idxs:
    #    print json.dumps((cmd, idx))
    max_term_freq = {}
    for (arg, cmd_cnts) in args.iteritems():
        for (cmd, cnt) in cmd_cnts.iteritems():
            if not cmd in max_term_freq:
                max_term_freq[cmd] = 0
            #max_term_freq[cmd] = max(max_term_freq[cmd], cnt)
            max_term_freq[cmd] += cnt
    #cmds = list(set(chain.from_iterable([v.keys() for v in args.values()])))
    cmds_idxs = zip(max_term_freq.items(), range(len(max_term_freq)))
    for ((cmd, f), idx) in cmds_idxs:
        print json.dumps((cmd, f, idx))

main()
