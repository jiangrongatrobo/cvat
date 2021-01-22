// Copyright (C) 2020 Intel Corporation
//
// SPDX-License-Identifier: MIT

import React from 'react';
import { useDispatch } from 'react-redux';
import Modal from 'antd/lib/modal';
import Menu from 'antd/lib/menu';
import { DownloadOutlined, LoadingOutlined } from '@ant-design/icons';
import Text from 'antd/lib/typography/Text';

import { deleteProjectAsync, exportProjectStatAsync } from 'actions/projects-actions';

interface Props {
    projectInstance: any;
    pending: boolean;
}

export default function ProjectActionsMenuComponent(props: Props): JSX.Element {
    const { projectInstance, pending } = props;

    const dispatch = useDispatch();

    const onDeleteProject = (): void => {
        Modal.confirm({
            title: `The project ${projectInstance.id} will be deleted`,
            content: 'All related data (images, annotations) will be lost. Continue?',
            className: 'cvat-modal-confirm-remove-project',
            onOk: () => {
                dispatch(deleteProjectAsync(projectInstance));
            },
            okButtonProps: {
                type: 'primary',
                danger: true,
            },
            okText: 'Delete',
        });
    };

    const onExportProjectStat = (): void => {
        dispatch(exportProjectStatAsync(projectInstance));
    }
    return (
        <Menu className='cvat-project-actions-menu'>
            <Menu.Item onClick={onExportProjectStat} key='project-downloader' disabled={pending} className='cvat-menu-download-project-stats-item'>
                <DownloadOutlined />
                <Text disabled={pending}>
                    Download Stats
                </Text>
                {pending && <LoadingOutlined style={{ marginLeft: 10 }} />}

            </Menu.Item>
            <hr />
            <Menu.Item onClick={onDeleteProject}>Delete</Menu.Item>
        </Menu>
    );
}
