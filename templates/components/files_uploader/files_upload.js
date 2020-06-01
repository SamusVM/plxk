'use strict';
import React from 'react';
import Files from 'react-files';
import 'static/css/files_uploader.css';
import NewFilesList from 'templates/components/files_uploader/new_files_list';

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
    const {fieldName} = this.props;
    return (
      <div className='mt-1'>
        <If condition={fieldName.length > 0}><div className='mr-2'>{fieldName}:</div></If>
        
        <If condition={this.props.files.length > 0}>
          <NewFilesList files={this.props.files} fileRemove={this.filesRemoveOne} />
        </If>
        <If condition={this.props.editable}>
          <Files
            ref='new_files'
            className='btn btn-sm btn-outline-secondary'
            // className='files-dropzone-list'
            // style={{height: '100px'}}
            onChange={this.onFilesChange}
            onError={this.onFilesError}
            multiple={this.props.multiple}
            maxFiles={10}
            maxFileSize={10000000}
            minFileSize={0}
            clickable
          >
            Додати файл(и)
          </Files>
        </If>
      </div>
    );
  }

  static defaultProps = {
    multiple: true,
    files: [],
    fieldName: '???',
    editable: true
  };
}

export default FilesUpload;