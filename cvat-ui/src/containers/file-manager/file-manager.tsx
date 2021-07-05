// Copyright (C) 2020-2021 Intel Corporation
//
// SPDX-License-Identifier: MIT

import React from 'react';
import { connect } from 'react-redux';

import { TreeNodeNormal } from 'antd/lib/tree/Tree';
import FileManagerComponent, { Files } from 'components/file-manager/file-manager';

import { loadShareDataAsync } from 'actions/share-actions';
import { ShareItem, CombinedState, Task } from 'reducers/interfaces';
import { getProjectsAsync } from 'actions/projects-actions';

interface OwnProps {
    ref: any;
    withRemote: boolean;
    onChangeActiveKey(key: string): void;
    projectId: number | null;
}

interface StateToProps {
    treeData: TreeNodeNormal[];
    tasks: Task[];
    fetching: boolean;
}

interface DispatchToProps {
    getTreeData(key: string, success: () => void, failure: () => void): void;
    getTasks: (projectId: number | null) => void;
}

function mapStateToProps(state: CombinedState): StateToProps {
    function convert(items: ShareItem[], path?: string): TreeNodeNormal[] {
        return items.map(
            (item): TreeNodeNormal => {
                const isLeaf = item.type !== 'DIR';
                const key = `${path}${item.name}${isLeaf ? '' : '/'}`;
                return {
                    key,
                    isLeaf,
                    title: item.name || 'root',
                    children: convert(item.children, key),
                };
            },
        );
    }

    const { root } = state.share;

    const { current } = state.tasks;
    const { fetching } = state.projects;

    return {
        treeData: convert([root], ''),

        tasks: current,
        fetching,
    };
}

function mapDispatchToProps(dispatch: any): DispatchToProps {
    return {
        getTreeData: (key: string, success: () => void, failure: () => void): void => {
            dispatch(loadShareDataAsync(key, success, failure));
        },
        getTasks: (id: number | null): void => {
            dispatch(
                getProjectsAsync({
                    id
                }),
            );
        },

    };
}

type Props = StateToProps & DispatchToProps & OwnProps;

export class FileManagerContainer extends React.PureComponent<Props> {
    private managerComponentRef: any;

    public getFiles(): Files {
        return this.managerComponentRef.getFiles();
    }

    public reset(): Files {
        return this.managerComponentRef.reset();
    }

    public render(): JSX.Element {
        const { treeData, getTreeData, withRemote, tasks, onChangeActiveKey, projectId, fetching, getTasks } = this.props;

        return (
            <FileManagerComponent
                treeData={treeData}
                onLoadData={getTreeData}
                onChangeActiveKey={onChangeActiveKey}
                withRemote={withRemote}
                ref={(component): void => {
                    this.managerComponentRef = component;
                }}

                tasks={tasks}
                fetching={fetching}
                getTasks={getTasks}
                projectId={projectId}
            />
        );
    }
}

export default connect(mapStateToProps, mapDispatchToProps, null, { forwardRef: true })(FileManagerContainer);
