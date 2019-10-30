'use strict';
import React, {Fragment} from 'react';
import Files from 'react-files';
import '../../_else/files_uploader.css';
import NewFilesList from '../../components/new_files_list';

class FilesUpload extends React.Component {
  onFilesChange = (new_files) => {
    const changed_event = {
      target: {
        name: 'files',
        value: new_files
      }
    };
    this.props.onChange(changed_event);
  };

  onFilesError = (error, file) => {
    console.log('error code ' + error.code + ': ' + error.message);
  };

  filesRemoveOne = (e, file) => {
    this.refs.new_files.removeFile(file);
  };

  render() {
    const {fieldName, oldFiles} = this.props;
    return (
      <>
        <div>{fieldName}:</div>
        <If condition={this.props.files.length > 0}>
          <NewFilesList files={this.props.files} fileRemove={this.filesRemoveOne} />
        </If>
          <Files
            ref='new_files'
            className='btn btn-sm btn-outline-secondary'
            // className='files-dropzone-list'
            // style={{height: '100px'}}
            onChange={this.onFilesChange}
            onError={this.onFilesError}
            multiple
            maxFiles={10}
            maxFileSize={10000000}
            minFileSize={0}
            clickable
          >
            Додати файл(и)
          </Files>
      </>
    );
  }

  static defaultProps = {
    oldFiles: [],
    files: [],
    fieldName: '???'
  };
}

export default FilesUpload;
