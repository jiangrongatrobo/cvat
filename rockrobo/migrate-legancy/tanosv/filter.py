# -*- coding: utf-8 -*-
# #%%
import os
import xml.etree.ElementTree as ET
import json
import argparse

# %%
"""
<annotation>
	<folder>JPEGImages</folder>
	<filename>StereoVision_E_L_1006154_-1_0_0_9266_324_-400_-89.jpeg</filename>
	<relpath>../JPEGImages/StereoVision_E_L_1006154_-1_0_0_9266_324_-400_-89.jpeg</relpath>
	<source>
		<database>Unknown</database>
	</source>
	<size>
		<width>1280</width>
		<height>960</height>
		<depth>3</depth>
	</size>
	<segmented>0</segmented>
	<object>
		<name>wire</name>
		<instance/>
		<pose>Unspecified</pose>
		<truncated>0</truncated>
		<group_of>0</group_of>
		<difficult>0</difficult>
		<dissemble>0</dissemble>
		<exposure>0</exposure>
		<shadow>0</shadow>
		<occlude>0</occlude>
		<bndbox>
			<xmin>807</xmin>
			<ymin>527</ymin>
			<xmax>997</xmax>
			<ymax>623</ymax>
		</bndbox>
	</object>
	<object>
		<name>folding chair</name>
		<instance/>
		<pose>Unspecified</pose>
		<truncated>0</truncated>
		<group_of>0</group_of>
		<difficult>0</difficult>
		<dissemble>0</dissemble>
		<exposure>0</exposure>
		<shadow>0</shadow>
		<occlude>0</occlude>
		<bndbox>
			<xmin>251</xmin>
			<ymin>315</ymin>
			<xmax>451</xmax>
			<ymax>538</ymax>
		</bndbox>
	</object>
	<lighting>daylight</lighting>
	<surface>dark wood floor</surface>
</annotation>
"""
def filter_unknown_labels(input_path, output_path, tgt_list):
  tree = ET.parse(input_path)
  root = tree.getroot()
  new_root = ET.Element(root.tag)
  skip_flg = False
  for elem in root:
    skip_flg = False
    if elem.tag == 'object':
      for att in elem:
        if att.tag == 'name':
          if att.text not in tgt_list:
            print('{} ||| unknown label: {}'.format(input_path, att.text))
            skip_flg=True
          break
    if not skip_flg:
      new_root.append(elem)

  ET.ElementTree(new_root).write(output_path)

  return

#%%
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--label_path', type=str, required=True)
    args = parser.parse_args()

    assert os.path.exists(args.input_dir)
    assert os.path.exists(args.label_path)
    if not os.path.exists(args.output_dir): os.mkdir(args.output_dir)

    tgt_list=[each['name'] for each in json.load(open(args.label_path))]

    for xml_file in os.listdir(args.input_dir):
      assert xml_file.endswith('.xml')
      filter_unknown_labels(os.path.join(args.input_dir, xml_file)
                            , os.path.join(args.output_dir, xml_file)
                            , tgt_list)

#%%
if __name__ == "__main__":
    main()
