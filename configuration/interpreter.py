"""
The Illuminator, a Energy System Integration Development kit 
    Copyright (C) 2024  Illuminator Team

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
    USA

    For questions and support, please contact us at illuminator@tudelft.nl
     
"""

import shutil

src_path_1 = r"Cases/Residential Case/connection.xml"
dst_path_1 = r"configuration/connection.xml"
shutil.copy(src_path_1, dst_path_1)
print('Copied',dst_path_1)

src_path_2 = r"Cases/Residential Case/config.xml"
dst_path_2 = r"configuration/config.xml"
shutil.copy(src_path_2, dst_path_2)
print('Copied',dst_path_2)
