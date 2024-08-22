import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class GraphService {
  constructor() {}

  private partnes = new Subject<any>();
  private complementary = new Subject<any>();

  orderGraph() {
    this.partnes.next();
  }

  orderGraphRequest(): Observable<any> {
    return this.partnes.asObservable();
  }

  infoGraph() {
    this.complementary.next();
  }

  infoGraphRequest(): Observable<any>{
    return this.complementary.asObservable();
  }
}
