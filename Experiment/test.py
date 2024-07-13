import numpy as np

# Assuming middle_rows_ele is defined as a list or numpy array of elements
middle_rows_ele = ['53000', '54000', '55000', '55500', '56000', '56500', '57000', '57500', '58000', '58500', '59000', '59500', '60000', '60500', '61000', '62000', '64000']

# Convert to numpy array if not already
middle_rows_arr = np.array(middle_rows_ele)

# Reshape to N * 1 array
reshaped_array = middle_rows_arr.reshape(len(middle_rows_arr), 1)

print(reshaped_array)
