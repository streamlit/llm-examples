## garantir que o provedor GitHub (Workload Identity Provider) possa impersonar o service account lulu-auth-service

### Conceder permissão ao principal federado para impersonar o service account
```
gcloud iam service-accounts add-iam-policy-binding lulu-auth-service@lulu-mvp.iam.gserviceaccount.com \
  --project=lulu-mvp \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/988538575854/locations/global/workloadIdentityPools/happy-kids-pool/attribute.repository/MVP-Psicologia-Positiva/lulu-teaches-mvp"
```
```
gcloud iam service-accounts add-iam-policy-binding lulu-auth-service@lulu-mvp.iam.gserviceaccount.com \
  --project=lulu-mvp \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/988538575854/locations/global/workloadIdentityPools/happy-kids-pool/attribute.sub/repo:MVP-Psicologia-Positiva/lulu-teaches-mvp"
```

### Confirmar que a política de IAM do service account
verificar se a permissão foi corretamente atribuída
```
gcloud iam service-accounts get-iam-policy lulu-auth-service@lulu-mvp.iam.gserviceaccount.com \
  --project=lulu-mvp
```