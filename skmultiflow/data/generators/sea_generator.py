__author__ = 'Guilherme Matsumoto'

from skmultiflow.data.base_instance_stream import BaseInstanceStream
from skmultiflow.core.base_object import BaseObject
import numpy as np


class SEAGenerator(BaseInstanceStream, BaseObject):
    """ SEAGenerator
    
    This generator is an implementation of the data stream with abrupt 
    concept drift, first described in Street and Kim's 'A streaming 
    ensemble algorithm (SEA) for large-scale classification'. 
    
    It generates 3 numerical attributes, that vary from 0 to 10, where 
    only 2 of them are relevant to the classification task. A classification 
    function is chosen, among four possible ones. These functions compare 
    the sum of the two relevant attributes with a threshold value, unique 
    for each of the classification functions. Depending on the comparison 
    the generator will classify an instance as one of the two possible 
    labels.
    
    Concept drift is possible if used in conjunction with the concept 
    drift generator, that at the time of this framework's first release 
    is not yet implemented. The abrupt drift is generated by changing 
    the classification function, thus changing the threshold.
    
    Two important features are the possibility to balance classes, which 
    means the class distribution will tend to a uniform one, and the possibility 
    to add noise, which will, according to some probability, change the chosen 
    label for an instance.
    
    Parameters
    ----------
    classification_function: int (Default: 0)
        Which of the four classification functions to use for the generation. 
        This value can vary from 0 to 3, and the thresholds are, 8, 9, 7 and 9.5.
         
    instance_seed: int (Default: 42)
        The seed used to initialize the random generator, which is an instance 
        of numpy's random.
        
    balance_classes: bool (Default: False)
        Whether to balance classes or not. If balanced, the class distribution 
        will converge to a uniform distribution.
        
    noise_percentage: float (Default: 0.0)
        The probability that noise will happen in the generation. At each 
        new sample generated, a random probability is generated, and if that 
        probability is higher than the noise_percentage, the chosen label will 
        be switched.
        
    Notes
    -----
    Concept drift is not yet available, since the support class that adds 
    the drift is not yet implemented.
    
    Examples
    --------
    >>> # Imports
    >>> from skmultiflow.data.generators.sea_generator import SEAGenerator
    >>> # Setting up the stream
    >>> stream = SEAGenerator(classification_function = 2, instance_seed = 112, balance_classes = False, 
    ... noise_percentage = 0.28)
    >>> stream.prepare_for_use()
    >>> # Retrieving one sample
    >>> stream.next_instance()
    (array([[ 3.75057129,  6.4030462 ,  9.50016579]]), array([ 0.]))
    >>> # Retrieving 10 samples
    >>> stream.next_instance(10)
    (array([[ 7.76929659,  8.32745763,  0.5480574 ],
       [ 8.85351458,  7.22346511,  0.02556032],
       [ 3.43419851,  0.94759888,  3.94642589],
       [ 7.3670683 ,  9.55806869,  8.20609371],
       [ 3.78544458,  7.84763615,  0.86231513],
       [ 1.6222602 ,  2.90069726,  0.45008172],
       [ 7.36533216,  8.39211485,  7.09361615],
       [ 9.8566856 ,  3.88003308,  5.03154482],
       [ 6.8373245 ,  7.21957381,  2.14152091],
       [ 0.75216155,  6.10890702,  4.25630425]]), array([ 1.,  1.,  1.,  1.,  1.,  0.,  0.,  1.,  1.,  1.]))
    >>> # Generators will have infinite remaining instances, so it returns -1
    >>> stream.estimated_remaining_instances()
    -1
    >>> stream.has_more_instances()
    True
    
    """
    def __init__(self, classification_function = 0, instance_seed = 42, balance_classes = False, noise_percentage = 0.0):
        super().__init__()

        #classification functions to use
        self.classification_functions = [self.classification_function_zero, self.classification_function_one,
                                         self.classification_function_two, self.classification_function_three]

        #default values
        self.num_numerical_attributes = 3
        self.num_nominal_attributes = 0
        self.num_values_per_nominal_att = 0
        self.num_classes = 2
        self.current_instance_x = None
        self.current_instance_y = None
        self.classification_function_index = None
        self.instance_seed = None
        self.balance_classes = None
        self.noise_percentage = None
        self.instance_random = None
        self.next_class_should_be_zero = False

        self.class_header = None
        self.attributes_header = None

        self.__configure(classification_function, instance_seed, balance_classes, noise_percentage)


    def __configure(self, classification_function, instance_seed, balance_classes, noise_percentage):
        self.classification_function_index = classification_function
        self.instance_seed = instance_seed
        self.balance_classes = balance_classes
        self.noise_percentage = noise_percentage
        self.instance_random = np.random
        self.instance_random.seed(self.instance_seed)
        self.next_class_should_be_zero = False

        self.class_header = ["class"]
        self.attributes_header = []
        for i in range(self.num_numerical_attributes):
            self.attributes_header.append("NumAtt" + str(i))


    def estimated_remaining_instances(self):
        return -1

    def has_more_instances(self):
        return True

    def next_instance(self, batch_size = 1):
        """ next_instance
        
        The sample generation works as follows: The three attributes are 
        generated with the random generator, initialized with the seed passed 
        by the user. Then, the classification function decides, as a function 
        of the two relevant attributes, whether to classify the instance as 
        class 0 or class 1. The next step is to verify if the classes should 
        be balanced, and if so, balance the classes. The last step is to add 
        noise, if the noise percentage is higher than 0.0.
        
        The generated sample will have 3 features, where only the two first 
        are relevant, and 1 label (it has one classification task).
        
        Parameters
        ----------
        batch_size: int
            The number of samples to return.
        
        Returns
        -------
        tuple or tuple list
            Return a tuple with the features matrix and the labels matrix for 
            the batch_size samples that were requested.
         
        """
        data = np.zeros([batch_size, self.num_numerical_attributes + 1])

        for j in range (batch_size):
            att1 = att2 = att3 = 0.0
            group = 0
            desired_class_found = False
            while not desired_class_found:
                att1 = 10*self.instance_random.rand()
                att2 = 10*self.instance_random.rand()
                att3 = 10*self.instance_random.rand()
                group = self.classification_functions[self.classification_function_index](att1, att2, att3)

                if not self.balance_classes:
                    desired_class_found = True
                else:
                    if ((self.next_class_should_be_zero & (group == 0)) | ((not self.next_class_should_be_zero) & (group == 1))):
                        desired_class_found = True
                        self.next_class_should_be_zero = not self.next_class_should_be_zero

            if ((0.01 + self.instance_random.rand() <= self.noise_percentage)):
                group = 1 if (group == 0) else 0

            data[j, 0] = att1
            data[j, 1] = att2
            data[j, 2] = att3
            data[j, 3] = group

            self.current_instance_x = data[j, :self.num_numerical_attributes]
            self.current_instance_y = data[j, self.num_numerical_attributes:]

        return (data[:, :self.num_numerical_attributes], data[:, self.num_numerical_attributes:].flatten())

    def prepare_for_use(self):
        self.restart()

    def is_restartable(self):
        return True

    def restart(self):
        self.instance_random.seed(self.instance_seed)
        self.next_class_should_be_zero = False

    def has_more_mini_batch(self):
        return True

    def get_num_nominal_attributes(self):
        return self.num_nominal_attributes

    def get_num_numerical_attributes(self):
        return self.num_numerical_attributes

    def get_num_values_per_nominal_attribute(self):
        return self.num_values_per_nominal_att

    def get_num_attributes(self):
        return self.num_numerical_attributes + (self.num_nominal_attributes * self.num_values_per_nominal_att)

    def get_num_targets(self):
        return self.num_classes

    def get_attributes_header(self):
        return self.attributes_header

    def get_classes_header(self):
        return self.class_header

    def get_last_instance(self):
        return (self.current_instance_x, self.current_instance_y)

    def classification_function_zero(self, att1, att2, att3):
        """ classification_function_zero
        
        Decides the sample class label based on the sum of att1 and att2, 
        and the threshold value of 8.
        
        Parameters
        ----------
        att1: float
            First numeric attribute.
            
        att2: float
            Second numeric attribute.
            
        att3: float
            Third numeric attribute.
        
        Returns
        -------
        int
            Returns the sample class label, either 0 or 1.
        
        """
        return 0 if (att1 + att2 <= 8) else 1

    def classification_function_one(self, att1, att2, att3):
        """ classification_function_one

        Decides the sample class label based on the sum of att1 and att2, 
        and the threshold value of 9.

        Parameters
        ----------
        att1: float
            First numeric attribute.

        att2: float
            Second numeric attribute.

        att3: float
            Third numeric attribute.

        Returns
        -------
        int
            Returns the sample class label, either 0 or 1.

        """
        return 0 if (att1 + att2 <= 9) else 1

    def classification_function_two(self, att1, att2, att3):
        """ classification_function_two

        Decides the sample class label based on the sum of att1 and att2, 
        and the threshold value of 7.

        Parameters
        ----------
        att1: float
            First numeric attribute.

        att2: float
            Second numeric attribute.

        att3: float
            Third numeric attribute.

        Returns
        -------
        int
            Returns the sample class label, either 0 or 1.

        """
        return 0 if (att1 + att2 <= 7) else 1

    def classification_function_three(self, att1, att2, att3):
        """ classification_function_three

        Decides the sample class label based on the sum of att1 and att2, 
        and the threshold value of 9.5.

        Parameters
        ----------
        att1: float
            First numeric attribute.

        att2: float
            Second numeric attribute.

        att3: float
            Third numeric attribute.

        Returns
        -------
        int
            Returns the sample class label, either 0 or 1.

        """
        return 0 if (att1 + att2 <= 9.5) else 1

    def get_plot_name(self):
        return "SEA Generator - " + str(self.num_classes) + " class labels"

    def get_classes(self):
        c = []
        for i in range(self.num_classes):
            c.append(i)
        return c

    def get_info(self):
        return 'SEAGenerator: classification_function: ' + str(self.classification_function_index) + \
               ' - instance_seed: ' + str(self.instance_seed) + \
               ' - balance_classes: ' + ('True' if self.balance_classes else 'False') + \
               ' - noise_percentage: ' + str(self.noise_percentage)

    def get_num_targeting_tasks(self):
        return 1

    def generate_drift(self):
        new_function = self.instance_random.randint(4)
        while new_function == self.classification_function_index:
            new_function = self.instance_random.randint(4)
        self.classification_function_index = new_function

if __name__ == "__main__":
    sg = SEAGenerator(classification_function=3, noise_percentage=0.2)

    X, y = sg.next_instance(10)
    print(X)
    print(y)
