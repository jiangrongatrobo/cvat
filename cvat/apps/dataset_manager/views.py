# Copyright (C) 2019-2020 Intel Corporation
#
# SPDX-License-Identifier: MIT

import os
import os.path as osp
import tempfile
from datetime import timedelta
from enum import Enum

import django_rq
from django.utils import timezone
import pandas as pd
from openpyxl.workbook.child import INVALID_TITLE_REGEX
import re

import cvat.apps.dataset_manager.task as task
from cvat.apps.engine.log import slogger
from cvat.apps.engine.models import Project, Task
from datumaro.cli.util import make_file_name
from datumaro.util import to_snake_case

from .formats.registry import EXPORT_FORMATS, IMPORT_FORMATS
from .util import current_function_name


_MODULE_NAME = __package__ + '.' + osp.splitext(osp.basename(__file__))[0]
def log_exception(logger=None, exc_info=True):
    if logger is None:
        logger = slogger
    logger.exception("[%s @ %s]: exception occurred" % \
            (_MODULE_NAME, current_function_name(2)),
        exc_info=exc_info)


def get_export_cache_dir(db_task):
    task_dir = osp.abspath(db_task.get_task_dirname())
    if osp.isdir(task_dir):
        return osp.join(task_dir, 'export_cache')
    else:
        raise Exception('Task dir {} does not exist'.format(task_dir))

DEFAULT_CACHE_TTL = timedelta(hours=10)
CACHE_TTL = DEFAULT_CACHE_TTL


def export_task(task_id, dst_format, server_url=None, save_images=False):
    try:
        db_task = Task.objects.get(pk=task_id)

        cache_dir = get_export_cache_dir(db_task)

        exporter = EXPORT_FORMATS[dst_format]
        output_base = '%s_%s' % ('dataset' if save_images else 'annotations',
            make_file_name(to_snake_case(dst_format)))
        output_path = '%s.%s' % (output_base, exporter.EXT)
        output_path = osp.join(cache_dir, output_path)

        task_time = timezone.localtime(db_task.updated_date).timestamp()
        if not (osp.exists(output_path) and \
                task_time <= osp.getmtime(output_path)):
            os.makedirs(cache_dir, exist_ok=True)
            with tempfile.TemporaryDirectory(dir=cache_dir) as temp_dir:
                temp_file = osp.join(temp_dir, 'result')
                task.export_task(task_id, temp_file, dst_format,
                    server_url=server_url, save_images=save_images)
                os.replace(temp_file, output_path)

            archive_ctime = osp.getctime(output_path)
            scheduler = django_rq.get_scheduler()
            cleaning_job = scheduler.enqueue_in(time_delta=CACHE_TTL,
                func=clear_export_cache,
                task_id=task_id,
                file_path=output_path, file_ctime=archive_ctime)
            slogger.task[task_id].info(
                "The task '{}' is exported as '{}' at '{}' "
                "and available for downloading for the next {}. "
                "Export cache cleaning job is enqueued, id '{}'".format(
                db_task.name, dst_format, output_path, CACHE_TTL,
                cleaning_job.id))

        return output_path
    except Exception:
        log_exception(slogger.task[task_id])
        raise

def export_task_as_dataset(task_id, dst_format=None, server_url=None):
    return export_task(task_id, dst_format, server_url=server_url, save_images=True)

class Metrics(Enum):
    Rectangle = "Rectangle"
    Tags = "Tags"
    Manually = "Manually"
    Total = "Total"
    def __str__(self):
        return self.value

def export_project_stats(tasks: list, db_project,  server_url=None):
    project_dir = osp.abspath(db_project.get_project_dirname())
    if osp.isdir(project_dir):
        cache_dir = osp.join(project_dir, 'export_cache')
        os.makedirs(cache_dir, exist_ok=True)
    else:
        raise Exception('Project dir {} does not exist'.format(project_dir))

    output_path = osp.join(cache_dir, 'stats.xlsx')

    xlsx = pd.ExcelWriter(output_path)
    labels =  dict((each['id'], each['name']) for each in list(db_project.label_set.values()))
    labels = dict((int(k),v) for k,v in labels.items())
    for (tid,tname) in tasks:
        db_ann = task.get_task_data(tid)
        struct = dict((v, dict((each.name, 0) for each in Metrics))
                      for v in list(labels.values()) + ["Total"])
        for each in db_ann['shapes']:
            source = each['source']
            type = each['type']
            label = labels[each['label_id']]

            if type == 'rectangle':
                struct[label][Metrics.Rectangle.name] += 1
                struct["Total"][Metrics.Rectangle.name] += 1
                if source == 'manual':
                    struct[label][Metrics.Manually.name] += 1
                    struct["Total"][Metrics.Manually.name] += 1
                struct[label][Metrics.Total.name] += 1
                struct["Total"][Metrics.Total.name] += 1

        for each in db_ann['tags']:
            source = each['source']
            label = labels[each['label_id']]

            struct[label][Metrics.Tags.name] += 1
            struct["Total"][Metrics.Tags.name] += 1
            if source == 'manual':
                struct[label][Metrics.Manually.name] += 1
                struct["Total"][Metrics.Manually.name] += 1
            struct[label][Metrics.Total.name] += 1
            struct["Total"][Metrics.Total.name] += 1

        struct_df = pd.DataFrame(struct).transpose()
        title="#{}_{}".format(tid, tname)
        title = re.sub(INVALID_TITLE_REGEX, '_', title)
        struct_df.to_excel(xlsx, sheet_name=title, index=True)
    xlsx.close()
    return output_path

def export_task_annotations(task_id, dst_format=None, server_url=None):
    return export_task(task_id, dst_format, server_url=server_url, save_images=False)

def clear_export_cache(task_id, file_path, file_ctime):
    try:
        if osp.exists(file_path) and osp.getctime(file_path) == file_ctime:
            os.remove(file_path)
            slogger.task[task_id].info(
                "Export cache file '{}' successfully removed" \
                .format(file_path))
    except Exception:
        log_exception(slogger.task[task_id])
        raise


def get_export_formats():
    return list(EXPORT_FORMATS.values())

def get_import_formats():
    return list(IMPORT_FORMATS.values())

def get_all_formats():
    return {
        'importers': get_import_formats(),
        'exporters': get_export_formats(),
    }