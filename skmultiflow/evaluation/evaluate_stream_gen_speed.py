__author__ = 'Guilherme Matsumoto'

from skmultiflow.core.base_object import BaseObject
from skmultiflow.core.utils.utils import dict_to_tuple_list
from timeit import default_timer as timer
import logging


class EvaluateStreamGenerationSpeed(BaseObject):
    """ EvaluateStreamGeneration
    
    Measures the stream's sample generation time.
    
    Parameters
    ----------
    num_samples: int (Default: 100000)
        The number of samples to generate.
    
    max_time: float (Default: float("inf"))
        The maximum simulation time.
    
    output_file: string, optional (Default: None)
        The name of the output file (Not yet implemented).
        
    batch_size: int (Default: 1)
        The number of samples to generate at a time.
    
    Examples
    --------
    >>> from skmultiflow.data.generators.random_rbf_generator_drift import RandomRBFGeneratorDrift
    >>> from skmultiflow.evaluation.evaluate_stream_gen_speed import EvaluateStreamGenerationSpeed
    >>> stream = RandomRBFGeneratorDrift(change_speed=0.2)
    >>> stream.prepare_for_use()
    >>> eval = EvaluateStreamGenerationSpeed(100000, float("inf"), None, 5)
    >>> stream = eval.eval(stream)
    Evaluation time: 110.064
    Generated 100000 samples
    Samples/second = 908.56
    
    """
    def __init__(self, num_samples=100000, max_time=float("inf"), output_file=None, batch_size=1):
        super().__init__()
        self.num_samples = num_samples
        self.max_time = max_time
        self.output_file = output_file
        self.batch_size = batch_size

    def eval(self, stream):
        """ eval
        
        This function will evaluate the stream passed as parameter.
        
        Parameters
        ----------
        stream: A stream (an extension from BaseInstanceStream) 
            The stream from which to draw the samples. 
        
        Returns
        -------
        BaseInstanceStream
            The used stream.
        
        """
        self._measure_stream_speed(stream)
        return stream

    def _measure_stream_speed(self, stream):
        logging.basicConfig(format='%(message)s', level=logging.INFO)
        sample_count = 0
        init_time = timer()
        true_percentage_index = 0
        logging.info('Measure generation speed of %s samples', str(self.num_samples))
        logging.info('Evaluating...')
        stream_local_max = float("inf") if (stream.estimated_remaining_instances() == -1) \
            else stream.estimated_remaining_instances()
        while ((timer() - init_time <= self.max_time) & (sample_count+self.batch_size <= self.num_samples)
               & (sample_count+self.batch_size <= stream_local_max)):
            sample = stream.next_instance(self.batch_size)
            sample_count += self.batch_size
            while (float(sample_count) + self.batch_size >= (((true_percentage_index+1)*self.num_samples)/20)):
                true_percentage_index += 1
                logging.info('%s%%', str(true_percentage_index*5))
        end_time = timer()
        logging.info('Evaluation time: %s', str(round(end_time - init_time, 3)))
        logging.info('Generated %s samples', str(sample_count))
        logging.info('Samples/second = %s', str(round(sample_count/(end_time-init_time), 3)))


    def set_params(self, dict):
        """ set_params

        This function allows the users to change some of the evaluator's parameters, 
        by passing a dictionary where keys are the parameters names, and values are 
        the new parameters' values.
        
        Parameters
        ----------
        dict: Dictionary
            A dictionary where the keys are the names of attributes the user 
            wants to change, and the values are the new values of those attributes.

        """
        params_list = dict_to_tuple_list(dict)
        for name, value in params_list:
            if name == 'num_samples':
                self.num_samples = value
            elif name == 'max_time':
                self.max_time = value
            elif name == 'output_file':
                self.output_file = value
            elif name == 'batch_size':
                self.batch_size = value

    def get_class_type(self):
        return 'estimator'

    def get_info(self):
        return 'EvaluateStreamGenerationSpeed: num_samples: ' + str(self.num_samples) + \
               ' - max_time: ' + (str(self.max_time)) + \
               ' - output_file: ' + (self.output_file if self.output_file is not None else 'None') + \
               ' - batch_size: ' + str(self.batch_size)

if __name__ == '__main__':
    msg = EvaluateStreamGenerationSpeed()
    print(msg.get_class_type())
    pass

