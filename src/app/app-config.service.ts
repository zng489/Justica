import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AppConfig } from './app-config.model';
import { tap } from 'rxjs/operators';

@Injectable()
export class AppConfigService {
  public static settings: AppConfig = null;

  constructor(private http: HttpClient) {}

  load(): Promise<AppConfig> {
    return Promise.resolve({
       name: null,
       production: true,
       api: null,
       authentication: null,
    });
  }
}
