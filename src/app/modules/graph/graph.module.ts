import { NgModule } from '@angular/core';

import { GraphRoutingModule } from './graph-routing.module';
import { GraphComponent } from './graph.component';
import { SharedModule } from '@shared/shared.module';
import { MatSidenavModule } from '@angular/material/sidenav';

@NgModule({
  declarations: [GraphComponent],
  imports: [
    SharedModule,
    GraphRoutingModule,
    MatSidenavModule,
  ],
  exports: [GraphComponent]
})
export class GraphModule { }
