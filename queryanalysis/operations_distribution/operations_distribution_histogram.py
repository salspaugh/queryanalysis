
import matplotlib.pyplot as plt
import numpy as np

from queryexplorer import connect_db

fontsize = 20.0

def main():
    data, labels = read_data_from_db()
    ind = range(len(data))
    width = 1.0
    bars = plt.bar(ind, data, width, edgecolor="green", color="white", hatch="//", linewidth=2.0)
    plt.xticks(rotation=90)
    plt.xticks([i+width/2 for i in ind], labels, size=fontsize)
    plt.yticks([])
    autolabel(bars)
    plt.ylabel("Number of Commands", size=fontsize)
    plt.show()

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                ha="center", va="bottom", size=fontsize-2.0)

def read_data_from_db():
    counts = []
    optypes = []
    db = connect_db()
    cursor = db.execute("select count(*) as count, operation_type from commands group by operation_type order by count")
    for (cnt, operation_type) in cursor.fetchall():
        if operation_type == "FilterSelection":
            operation_type = "Filter"
        if operation_type == "InputtingSelection":
            operation_type = "Input"
        if operation_type == "TransformingProjection":
            operation_type = "Transform"
        if operation_type == "Projection":
            operation_type = "Project"
        if operation_type == "ExtendedProjection":
            operation_type = "Extend"
        if operation_type == "WindowingProjection":
            operation_type = "Window"
        if operation_type == "Aggregation":
            operation_type = "Aggregate"
        counts.append(cnt)
        optypes.append(operation_type)
    db.close()    
    return counts, optypes

def read_data_from_csv():
    with open('/Users/salspaugh/queryexplorer/data/operations_hierarchy/category_counts_unique_commands_unique_queries.csv') as file:
        data = []
        labels = []
        first = True
        for line in file.readlines():
            parts = line.split(',')
            if first:
                first = False
                continue
            data.append(int(parts[0].strip()))
            labels.append(parts[1].strip())
    return data, labels

main()
