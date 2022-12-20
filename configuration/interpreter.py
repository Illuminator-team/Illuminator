
import shutil

src_path_1 = r"Cases/Residential Case/connection.xml"
dst_path_1 = r"configuration/connection.xml"
shutil.copy(src_path_1, dst_path_1)
print('Copied',dst_path_1)

src_path_2 = r"Cases/Residential Case/config.xml"
dst_path_2 = r"configuration/config.xml"
shutil.copy(src_path_2, dst_path_2)
print('Copied',dst_path_2)
