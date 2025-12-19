import os
import pandas as pd
import random
from typing import List

class DataLoadingError(Exception) :
    pass

class InvalidTrailError(Exception) :
    pass

class ProductRecord :
    def __init__(
        self,
        product_id : str,
        is_defective : bool,
        weight_g : float,
        length_mm : float,
        batch_id : str,
        machine_id : str,
        timestamp
    ) :
        self.product_id = product_id
        self.is_defective = is_defective
        self.weight_g = weight_g
        self.length_mm = length_mm 
        self.batch_id = batch_id
        self.machine_id = machine_id
        self.timestamp = timestamp
        
class ManufacturingDataSet : 
    REQUIRED_COLUMNS = {
        "product_id",
        "is_defective",
        "weight_g",
        "length_mm",
        "batch_id",
        "machine_id",
        "timestamp"
    }
    
    def __init__(self, inFilePath : str) :
        self.inFilePath = inFilePath
        self.records = List[ProductRecord] = []
    