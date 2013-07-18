
class Context(object):      # of argument foo

    def __init__(self, arg):
        self.arg = arg
        self.grp_filtered_on_as_value = 0
        self.grp_filtered_on_as_field = 0
        self.grp_argument_to_top = 0
        self.grp_projected = 0
        self.grp_unprojected = 0
        self.grp_grouped_by = 0
        self.grp_argument_renamed_as = 0
        self.grp_argument_to_aggregation = 0
        self.grp_argument_to_arithmetic_transformation = 0
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
        return ([getattr(self, attr) for attr in self.contexts] 
                    < [getattr(other, attr) for attr in other.contexts])

    def __eq__(self, other):
        return ([getattr(self, attr) for attr in self.contexts] 
                    == [getattr(other, attr) for attr in other.contexts])

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
        return [(attr.replace("grp_", "").replace("_"," "), getattr(self, attr)) 
                    for attr in self.contexts]

    def get_labels(self):
        return [s.replace("grp_", "").replace("_", " ") for s in self.contexts]

    def get_colors(self):
        return self.colors

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
