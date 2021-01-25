// Copyright (C) 2020 Intel Corporation
//
// SPDX-License-Identifier: MIT

import { connect } from 'react-redux';

import { CombinedState, Project } from 'reducers/interfaces';
import AdvancedConfigurationForm from 'components/create-task-page/advanced-configuration-form';
import {getProjectsAsync} from 'actions/projects-actions'

interface StateToProps {
    projects: Project[];
    fetching: boolean;
}

interface DispatchToProps {
  getLabels: (projectId: number | null) => void;
}

function mapDispatchToProps(dispatch: any): DispatchToProps {
  return {
    getLabels: (projectId: number | null): void => dispatch(getProjectsAsync({id: projectId})),
  };
}

function mapStateToProps(state: CombinedState): StateToProps {
    const { fetching } = state.projects;
    const { current } = state.projects;
    return {
        projects: current,
        fetching,
    };
}

export default connect(mapStateToProps, mapDispatchToProps, null, { forwardRef: true })(AdvancedConfigurationForm);