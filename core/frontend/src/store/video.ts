import axios from 'axios'
import {
  Action, getModule, Module, Mutation, VuexModule,
} from 'vuex-module-decorators'

import store from '@/store'
import NotificationStore from '@/store/notifications'
import { video_manager_service } from '@/types/frontend_services'
import { LiveNotification, NotificationLevel } from '@/types/notifications'
import { CreatedStream, Device, StreamStatus } from '@/types/video'

const notification_store: NotificationStore = getModule(NotificationStore)

@Module({
  dynamic: true,
  store,
  name: 'video',
})

@Module
class VideoStore extends VuexModule {
  API_URL = '/mavlink-camera-manager'

  available_streams: StreamStatus[] = []

  available_devices: Device[] = []

  updating_streams = true

  updating_devices = true

  @Mutation
  setUpdatingStreams(updating: boolean): void { this.updating_streams = updating }

  @Mutation
  setUpdatingDevices(updating: boolean): void { this.updating_devices = updating }

  @Mutation
  setAvailableStreams(available_streams: StreamStatus[]): void {
    this.available_streams = available_streams
    this.updating_streams = false
  }

  @Mutation
  setAvailableDevices(available_devices: Device[]): void {
    this.available_devices = available_devices
    this.updating_devices = false
  }

  @Action
  async deleteStream(stream: StreamStatus): Promise<void> {
    this.setUpdatingStreams(true)

    await axios({
      method: 'delete',
      url: `${this.API_URL}/delete_stream`,
      timeout: 10000,
      params: { name: stream.video_and_stream.name },
    })
      .catch((error) => {
        notification_store.pushNotification(new LiveNotification(
          NotificationLevel.Error,
          video_manager_service,
          'VIDEO_STREAM_DELETE_FAIL',
          `Could not delete video stream: ${error.message}.`,
        ))
      })
  }

  @Action
  async createStream(stream: CreatedStream): Promise<boolean> {
    this.setUpdatingStreams(true)

    return axios({
      method: 'post',
      url: `${this.API_URL}/streams`,
      timeout: 10000,
      data: stream,
    })
      .then(() => true)
      .catch((error) => {
        notification_store.pushNotification(new LiveNotification(
          NotificationLevel.Error,
          video_manager_service,
          'VIDEO_STREAM_CREATION_FAIL',
          `Could not create video stream: ${error.message}.`,
        ))
        return false
      })
  }
}

export { VideoStore }

const video: VideoStore = getModule(VideoStore)
export default video
