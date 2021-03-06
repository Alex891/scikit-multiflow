__author__ = 'Guilherme Matsumoto'

from sklearn.linear_model.stochastic_gradient import SGDClassifier, SGDRegressor
from sklearn.linear_model.passive_aggressive import PassiveAggressiveClassifier
from sklearn.linear_model.perceptron import Perceptron
from skmultiflow.classification.perceptron import PerceptronMask
from skmultiflow.classification.lazy.knn_adwin import KNNAdwin
from skmultiflow.classification.lazy.knn import KNN
from skmultiflow.classification.meta.oza_bagging_adwin import OzaBaggingAdwin
from skmultiflow.core.pipeline import Pipeline
from skmultiflow.data.file_stream import FileStream
from skmultiflow.options.file_option import FileOption
from skmultiflow.data.generators.waveform_generator import WaveformGenerator
from skmultiflow.evaluation.evaluate_prequential import EvaluatePrequential


def demo(output_file=None, instances=40000):
    """ _test_prequential
    
    This demo shows how to produce a prequential evaluation.
    
    The first thing needed is a stream. For this case we use a file stream 
    which gets its samples from the sea_big.csv file, inside the datasets 
    folder.
    
    Then we need to setup a classifier, which in this case is an instance 
    of sklearn's PassiveAggressiveClassifier. Then, optionally we create a 
    pipeline structure, initialized on that classifier.
    
    The evaluation is then run.
    
    Parameters
    ----------
    output_file: string
        The name of the csv output file
    
    instances: int
        The evaluation's max number of instances
    
    """
    # Setup the File Stream
    #opt = FileOption("FILE", "OPT_NAME", "../datasets/covtype.csv", "CSV", False)
    opt = FileOption("FILE", "OPT_NAME", "../datasets/sea_big.csv", "CSV", False)
    stream = FileStream(opt, -1, 1)
    #stream = WaveformGenerator()
    stream.prepare_for_use()

    # Setup the classifier
    #classifier = SGDClassifier()
    # classifier = KNNAdwin(k=8, max_window_size=2000,leaf_size=40, categorical_list=None)
    #classifier = OzaBaggingAdwin(h=KNN(k=8, max_window_size=2000, leaf_size=30, categorical_list=None))
    classifier = PassiveAggressiveClassifier()
    #classifier = SGDRegressor()
    #classifier = PerceptronMask()

    # Setup the pipeline
    pipe = Pipeline([('Classifier', classifier)])

    # Setup the evaluator
    eval = EvaluatePrequential(pretrain_size=200, max_instances=instances, batch_size=1, n_wait=100, max_time=1000,
                               output_file=output_file, task_type='classification', show_plot=True,
                               plot_options=['kappa', 'kappa_t', 'performance'])

    # Evaluate
    eval.eval(stream=stream, classifier=pipe)

if __name__ == '__main__':
    demo('log_test_prequential.csv', 20000)