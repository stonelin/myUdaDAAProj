import matplotlib.pyplot as plt


def draw(features, names=None, draw_index=(0, 1)):
    for feature in features:
        plt.scatter(feature[draw_index[0]], features[draw_index[1]], color = "b")
    if names:
        plt.xlabel(names[0])
        plt.ylabel(names[1])
    plt.show()