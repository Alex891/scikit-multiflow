__author__ = 'Guilherme Matsumoto'

from skmultiflow.core.base_object import BaseObject


class InstanceHeader(BaseObject):
    """ InstanceHeader
    
    Stores the header from an instance, simply keeps feature and 
    label's names
    
    Parameters
    ----------
    header: list, optional
        The entries of the header.
        
    """

    def __init__(self, header = None):
        super().__init__()
        self.header = header
        pass

    def get_header_label_at(self, header_index = -1):
        """ get_header_label_at
        
        Gets the header label at index header_index.
        
        Parameters
        ----------
        header_index: int
            An index from the instance header.
        
        Returns
        -------
        string
            The index label.
        
         
        """
        if self.header is not None:
            return self.header[header_index] if ((header_index > -1) and (header_index < len(self.header))) else None
        else:
            return None

    def get_class_type(self):
        return 'instance'

    def get_info(self):
        return 'InstanceHeader: header: ' + str(self.header)
