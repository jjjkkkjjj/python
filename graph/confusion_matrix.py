import matplotlib.pyplot as plt
import numpy as np
import itertools

def plot_confusion_matrix(cm,
                          target_names,
                          title='Confusion matrix',
                          cmap=None,
                          normalize=True):
    """
    given a sklearn confusion matrix (cm), make a nice plot

    Arguments
    ---------
    cm:           confusion matrix from sklearn.metrics.confusion_matrix

    target_names: given classification classes such as [0, 1, 2]
                  the class names, for example: ['high', 'medium', 'low']

    title:        the text to display at the top of the matrix

    cmap:         the gradient of the values displayed from matplotlib.pyplot.cm
                  see http://matplotlib.org/examples/color/colormaps_reference.html
                  plt.get_cmap('jet') or plt.cm.Blues

    normalize:    If False, plot the raw numbers
                  If True, plot the proportions

    Usage
    -----
    plot_confusion_matrix(cm           = cm,                  # confusion matrix created by
                                                              # sklearn.metrics.confusion_matrix
                          normalize    = True,                # show proportions
                          target_names = y_labels_vals,       # list of names of the classes
                          title        = best_estimator_name) # title of graph

    Citiation
    ---------
    http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html

    """
    size = 24
    accuracy = np.trace(cm) / float(np.sum(cm))
    precision = float(cm[0,0]) / (cm[0,0] + cm[0,1])
    recall = float(cm[0,0]) / (cm[0,0] + cm[1,0])
    F = 2*recall*precision/(recall + precision)
    misclass = 1 - accuracy


    if cmap is None:
        cmap = plt.get_cmap('Blues')

    #plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title("", fontsize=size)
    plt.colorbar().ax.tick_params(labelsize=size)

    if target_names is not None:
        tick_marks = np.arange(len(target_names))
        plt.xticks(tick_marks, target_names, fontsize=size)
        plt.yticks(tick_marks, target_names, fontsize=size)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]


    thresh = cm.max() / 1.5 if normalize else cm.max() / 2
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        if normalize:
            plt.text(j, i, "{:0.4f}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")
        else:
            plt.text(j, i, "{:,}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black", fontsize=size)


    plt.ylabel('True label', fontsize=size)
    plt.xlabel('\nPredicted label\n\naccuracy={:0.2f}, precision={:0.2f}, \nrecall={:0.2f}, F-measure={:0.2f}'.format(accuracy, precision, recall, F), fontsize=size)
    plt.tight_layout()
    plt.show()


plot_confusion_matrix(np.array([[21, 10],
                                [3, 17]]), target_names=['positive', 'negative'], normalize=False)