import { NgModule } from '@angular/core';
import { Routes, RouterModule, PreloadAllModules } from '@angular/router';
import { EnvService } from './services/env.service';

// Força o carregamento das variáveis de ambiente
const env = new EnvService();

const routes: Routes = [
  {
    path: '',
    redirectTo: 'graph',
    pathMatch: 'full',
  },
  {
    path: 'graph',
    loadChildren: () =>
      import('src/app/modules/graph/graph.module').then((m) => m.GraphModule),
    runGuardsAndResolvers: 'always',
    data: {
      allowedTypes: ['noshellnobreadcrumb'],
      defaultType: 'noshellnobreadcrumb'
    }
  },
  { path: '**', redirectTo: 'not-found' }, // NotFoundComponent está no UiKit (assim como sua rota)

  /*  Layout options
   data: {
     allowedTypes: ['normal', 'noshell', 'noshellnobreadcrumb'],
     defaultType: 'normal'
   }
  */
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes, {
      paramsInheritanceStrategy: 'always',
      onSameUrlNavigation: 'reload',
      preloadingStrategy: PreloadAllModules,
    }),
  ],
  exports: [RouterModule],
})
export class AppRoutingModule {}
